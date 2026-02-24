"""Pygame-based main loop for the D&D roguelike.

Replaces the terminal version with a visual battle grid.
"""
import random
import argparse
import pygame
from character import Character
from creator import create_character_interactive
from character_creator_gui import select_character_gui
from waves import spawn_wave
from class_definitions import generate_level_1_stats
from keep_management import KeepState
from gui import (
    GameWindow,
    KEEP_START_X,
    KEEP_START_Y,
    KEEP_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    GATE_X,
    GATE_Y,
    GATE_WIDTH,
)
import dice
import math


class GameState:
    """Manages game state including character positions."""
    
    def __init__(self, player: Character, keep_state: KeepState | None = None, level_one_focus: bool = False):
        self.player = player
        self.keep_state = keep_state
        self.level_one_focus = level_one_focus
        self.player_pos = (KEEP_START_X + KEEP_SIZE // 2, KEEP_START_Y + KEEP_SIZE // 2)
        self.enemies = []
        self.enemy_positions = {}  # enemy -> (x, y)
        self.selected_target = None
        self.message = ""
        self.message_timer = 0
        self.combat_log = []
        self.turn_phase = "player_input"  # "player_input" or "processing"
        self.pause_frames = 0  # Frames to pause before next action
        self.round_number = 0
        # Action economy tracking
        self.actions_remaining = 1
        self.spent_action = False  # True if standard action used
        self.spent_bonus_action = False  # True if bonus action used
        # Visibility/stealth tracking
        self.hidden = False  # True if player is currently hidden
        self.hidden_stealth_total: int | None = None
        self.last_known_player_pos = self.player_pos  # Where enemies last saw the player
        self.sneak_attack_used_this_turn = False  # True if sneak attack already used
        self.hidden_enemies: set = set()  # Enemies currently in stealth
        self.targeting_mode = False
        self.targeting_action: str | None = None
        self.spell_menu_open = False
        self.movement_max = max(1, self.player.get_speed_ft() // 5)
        self.movement_used = 0
        self.player_turn_started = False
        self.trees = set()  # Provide cover but don't block movement
        self.rocks = set()  # Provide cover and block movement
        self.obstacles = set()  # Blocking tiles (rocks only)
        self.wave_gold_gained = 0
        self.wave_xp_gained = 0
        self.wave_item_drops = []
        self.banked_xp_total = 0
        self.pending_level_up_events: list[dict[str, object]] = []
        self.cleave_used_this_turn = False
        self.nick_used_this_turn = False
        self.pending_on_hit_actions: dict[str, dict] = {}
        # Reaction economy (one reaction per round, resets at start of turn)
        self.reaction_used = False
        # Trigger queue: list of dicts with keys:
        #   title, description, accept_label, decline_label,
        #   on_accept (callable), on_decline (callable or None)
        self.pending_triggers: list[dict] = []
        self._trigger_resume_phase: str = "player_input"
        # Processing sub-phases for interruptible enemy turn
        self._processing_subphase: str = "idle"  # idle, post_movement, resolving_enemies, done
        self._enemy_turn_index: int = 0  # Which enemy is currently acting
        # Fog of war / vision
        self.raid_sides: list[str] = []  # e.g. ['north', 'east']
        self._visible_cells: set[tuple[int, int]] = set()
        self.compute_player_visibility()

    def _apply_enemy_defeat_rewards(self, enemy: Character) -> tuple[int, int, str | None]:
        gold_gain = max(0, int(getattr(enemy, "bounty", 0)))
        xp_gain = gold_gain * 10
        self.player.gold += gold_gain
        if self.level_one_focus:
            self.banked_xp_total += xp_gain
        else:
            old_level = int(self.player.level)
            levels_gained = int(self.player.add_xp(xp_gain))
            if levels_gained > 0:
                new_level = int(self.player.level)
                unlocked_features = []
                if hasattr(self.player, "get_newly_unlocked_features"):
                    unlocked_features = self.player.get_newly_unlocked_features(old_level, new_level)
                self.pending_level_up_events.append(
                    {
                        "from_level": old_level,
                        "to_level": new_level,
                        "features": list(unlocked_features),
                    }
                )
                self.add_log(f"Level Up! {self.player.name} reached level {new_level}.")
                for feature_name in unlocked_features:
                    self.add_log(f"New feature unlocked: {feature_name}.")
        self.wave_gold_gained += gold_gain
        self.wave_xp_gained += xp_gain
        self.add_log(f"Looted {gold_gain} gold.")
        if self.level_one_focus:
            self.add_log(f"Gained {xp_gain} XP (banked; level-ups disabled).")
        else:
            self.add_log(f"Gained {xp_gain} XP.")

        item_drop = None
        if random.randint(1, 100) <= 30:
            from items import create_potion_of_healing
            potion = create_potion_of_healing()
            self.player.add_item(potion)
            item_drop = str(getattr(potion, "name", "Potion of Healing"))
            self.wave_item_drops.append(item_drop)
            self.add_log(f"Found {item_drop}.")
        return gold_gain, xp_gain, item_drop

    def wave_loot_lines(self) -> list[str]:
        lines = [
            f"Gold gained: {self.wave_gold_gained}",
            f"XP gained: {self.wave_xp_gained}",
        ]
        if self.level_one_focus:
            lines.append(f"Level-1 focus: XP banked total {self.banked_xp_total}")
        if self.wave_item_drops:
            counts = {}
            for item_name in self.wave_item_drops:
                counts[item_name] = counts.get(item_name, 0) + 1
            for item_name, count in sorted(counts.items()):
                lines.append(f"Item: {item_name} x{count}")
        else:
            lines.append("Items: None")
        return lines
        
    # ------------------------------------------------------------------
    # Lighting helpers
    # ------------------------------------------------------------------

    #: Chebyshev distance from the keep walls within which cells are
    #: considered *well-lit* (matching the obstacle-free clearing).
    LIGHT_RADIUS = 6

    def is_cell_lit(self, x: int, y: int) -> bool:
        """Return True if a cell is well-lit (inside the keep or clearing).

        The raid happens at night so only the keep interior and the
        cleared ring around it have light sources.
        """
        # Inside the keep?
        if (KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE
                and KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE):
            return True
        # Inside the lit clearing around the keep?
        dx = 0
        if x < KEEP_START_X:
            dx = KEEP_START_X - x
        elif x > KEEP_START_X + KEEP_SIZE - 1:
            dx = x - (KEEP_START_X + KEEP_SIZE - 1)
        dy = 0
        if y < KEEP_START_Y:
            dy = KEEP_START_Y - y
        elif y > KEEP_START_Y + KEEP_SIZE - 1:
            dy = y - (KEEP_START_Y + KEEP_SIZE - 1)
        return max(dx, dy) < self.LIGHT_RADIUS

    def get_lit_cells(self) -> set[tuple[int, int]]:
        """Return the set of all grid cells that are well-lit.

        Cached after first call since the lit zone never changes mid-game.
        """
        if not hasattr(self, "_lit_cells_cache"):
            lit: set[tuple[int, int]] = set()
            # The lit zone extends LIGHT_RADIUS cells from the keep walls.
            x_lo = max(0, KEEP_START_X - self.LIGHT_RADIUS)
            x_hi = min(GRID_WIDTH - 1, KEEP_START_X + KEEP_SIZE - 1 + self.LIGHT_RADIUS)
            y_lo = max(0, KEEP_START_Y - self.LIGHT_RADIUS)
            y_hi = min(GRID_HEIGHT - 1, KEEP_START_Y + KEEP_SIZE - 1 + self.LIGHT_RADIUS)
            for x in range(x_lo, x_hi + 1):
                for y in range(y_lo, y_hi + 1):
                    if self.is_cell_lit(x, y):
                        lit.add((x, y))
            self._lit_cells_cache = lit
        return self._lit_cells_cache

    # ------------------------------------------------------------------
    # Fog of war / vision helpers
    # ------------------------------------------------------------------

    #: Minimum cells a character can always see around themselves (torch
    #: range / ambient light in darkness).
    DARK_VISION_MIN = 2

    def _player_vision_range(self) -> int:
        """Calculate player vision range in grid cells.

        Formula: base 10 + Perception skill bonus + darkvision_range/5.
        This gives humans ~11-14 cells and darkvision species ~23-27 cells.
        """
        base = 10
        perception_bonus = self.player.get_skill_bonus("Perception")
        base += max(0, perception_bonus)
        darkvision_ft = int(getattr(self.player, "darkvision_range", 0) or 0)
        base += max(0, darkvision_ft // 5)
        return base

    def _player_dark_vision_range(self) -> int:
        """Vision range when looking *into* unlit cells.

        Characters without darkvision can only see ``DARK_VISION_MIN``
        cells into darkness.  Darkvision extends this to
        darkvision_range / 5.
        """
        darkvision_ft = int(getattr(self.player, "darkvision_range", 0) or 0)
        dv_cells = max(0, darkvision_ft // 5)
        if dv_cells > 0:
            return dv_cells
        return self.DARK_VISION_MIN

    def compute_player_visibility(self) -> set[tuple[int, int]]:
        """Recompute which cells the player can currently see.

        Uses Chebyshev distance for range, then Bresenham LOS checks.
        Unlit cells beyond the player's dark-vision range are hidden
        even if they would otherwise be in normal vision range.
        Results are cached in ``_visible_cells``.
        """
        px, py = self.player_pos
        vision = self._player_vision_range()
        dark_range = self._player_dark_vision_range()
        player_lit = self.is_cell_lit(px, py)
        visible: set[tuple[int, int]] = set()
        x_lo = max(0, px - vision)
        x_hi = min(GRID_WIDTH - 1, px + vision)
        y_lo = max(0, py - vision)
        y_hi = min(GRID_HEIGHT - 1, py + vision)
        for x in range(x_lo, x_hi + 1):
            for y in range(y_lo, y_hi + 1):
                dist = max(abs(x - px), abs(y - py))
                if dist > vision:
                    continue
                # Determine effective range for this cell
                cell_lit = self.is_cell_lit(x, y)
                if not cell_lit and not player_lit:
                    # Both in darkness – limited to dark vision range
                    if dist > dark_range:
                        continue
                elif not cell_lit:
                    # Player is lit, looking into darkness
                    if dist > dark_range:
                        continue
                # Adjacent cells are always visible
                if dist <= 1:
                    visible.add((x, y))
                    continue
                if self._has_line_of_sight((px, py), (x, y)):
                    visible.add((x, y))
        self._visible_cells = visible
        return visible

    def is_cell_visible(self, x: int, y: int) -> bool:
        """Return True if the player can currently see the cell.

        Lazily recomputes visibility if the cache is stale (e.g. player_pos
        was set directly without going through move_player).
        """
        if self.player_pos not in self._visible_cells:
            self.compute_player_visibility()
        return (x, y) in self._visible_cells

    def _spawn_position_for_side(self, side: str) -> tuple[int, int]:
        """Return a random spawn position along a map edge."""
        edge_depth = 3
        if side == "north":
            return (random.randint(0, GRID_WIDTH - 1), random.randint(0, edge_depth - 1))
        elif side == "south":
            return (random.randint(0, GRID_WIDTH - 1), random.randint(GRID_HEIGHT - edge_depth, GRID_HEIGHT - 1))
        elif side == "east":
            return (random.randint(GRID_WIDTH - edge_depth, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        elif side == "west":
            return (random.randint(0, edge_depth - 1), random.randint(0, GRID_HEIGHT - 1))
        # Fallback
        return (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))

    def _generate_horn_blast_message(self) -> str:
        """Return a thematic horn-blast message for the current raid_sides."""
        names = [s.capitalize() for s in self.raid_sides]
        if len(names) == 1:
            return f"War horns sound from the {names[0]}!"
        elif len(names) == 2:
            return f"War horns sound from the {names[0]} and {names[1]}!"
        else:
            return f"War horns sound from the {', '.join(names[:-1])}, and {names[-1]}!"

    def add_enemies(self, enemies: list):
        """Add enemies and place them along 1-3 random map edges.

        Always leaves at least one side clear so kiting classes (Rogues,
        Rangers) have room to manoeuvre.
        """
        self.enemies = enemies
        self._generate_obstacles()

        # Pick 1-3 raid sides, leaving at least one free
        all_sides = ["north", "south", "east", "west"]
        num_sides = random.randint(1, 3)
        self.raid_sides = random.sample(all_sides, num_sides)

        for enemy in enemies:
            side = random.choice(self.raid_sides)
            x, y = self._spawn_position_for_side(side)
            # Keep trying until we get a valid position
            while (KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE and
                   KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE) or (x, y) in self.rocks:
                x, y = self._spawn_position_for_side(side)
            self.enemy_positions[enemy] = (x, y)
            # Sneaky enemies start hidden
            if getattr(enemy, "behavior", "") == "sneaky":
                self.hidden_enemies.add(enemy)

        self.compute_player_visibility()

    def _generate_obstacles(self):
        """Generate obstacles: trees (cover only) and rocks (cover + blocking)."""
        candidates = []
        min_gap = 6
        # Cover whole map instead of just a radius around keep
        min_x = 0
        max_x = GRID_WIDTH - 1
        min_y = 0
        max_y = GRID_HEIGHT - 1
        gate_cells = {(x, GATE_Y) for x in range(GATE_X, GATE_X + GATE_WIDTH)}

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE and KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE:
                    continue
                if (x, y) in gate_cells:
                    continue
                dx = 0
                if x < KEEP_START_X:
                    dx = KEEP_START_X - x
                elif x > KEEP_START_X + KEEP_SIZE - 1:
                    dx = x - (KEEP_START_X + KEEP_SIZE - 1)
                dy = 0
                if y < KEEP_START_Y:
                    dy = KEEP_START_Y - y
                elif y > KEEP_START_Y + KEEP_SIZE - 1:
                    dy = y - (KEEP_START_Y + KEEP_SIZE - 1)
                if max(dx, dy) < min_gap:
                    continue
                candidates.append((x, y))

        total_count = int(len(candidates) * 0.15)
        if total_count > 0:
            selected = random.sample(candidates, k=total_count)
            # 70% trees, 30% rocks
            rock_count = int(total_count * 0.3)
            self.rocks = set(selected[:rock_count])
            self.trees = set(selected[rock_count:])
        else:
            self.trees = set()
            self.rocks = set()
        self.obstacles = set(self.rocks)

    @staticmethod
    def _tree_blocks_los(tx: int, ty: int) -> bool:
        """Return True if a tree at (tx, ty) is dense enough to block LOS.

        Uses a deterministic hash so ~50% of trees block sight while the
        result stays stable across frames.
        """
        return hash((tx, ty)) % 2 == 0

    def _has_line_of_sight(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
        """Return True if there is a clear line of sight between two cells.

        Rocks always block LOS.  Trees block LOS ~50% of the time
        (determined by a stable per-position hash).
        """
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0

        while (x, y) != (x1, y1):
            if (x, y) not in (start, end):
                if (x, y) in self.rocks:
                    return False
                if (x, y) in self.trees and self._tree_blocks_los(x, y):
                    return False
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return True

    def _cover_bonus(self, attacker_pos: tuple[int, int], target_pos: tuple[int, int]) -> int:
        """Return cover AC bonus between attacker and target per SRD 5.2.1.

        Cover only applies when an obstacle lies on the line between
        attacker and target (i.e. on the opposite side of the target).

        - Trees -> Half Cover (+2 AC)
        - Rocks -> Three-Quarters Cover (+5 AC)

        Only the most protective degree applies (they don't stack).
        """
        # Collect obstacles that lie between attacker and target
        best = 0
        ax, ay = attacker_pos
        tx, ty = target_pos
        dx = abs(tx - ax)
        dy = abs(ty - ay)
        sx = 1 if ax < tx else -1
        sy = 1 if ay < ty else -1
        err = dx + (-abs(dy))
        x, y = ax, ay
        while (x, y) != (tx, ty):
            if (x, y) != attacker_pos:
                if (x, y) in self.rocks:
                    best = max(best, 5)  # Three-Quarters Cover
                elif (x, y) in self.trees:
                    best = max(best, 2)  # Half Cover
            e2 = 2 * err
            if e2 >= -abs(dy):
                err += -abs(dy)
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        # Also check obstacles adjacent to target (providing cover from that side)
        for ox, oy in self.rocks:
            if (ox, oy) == target_pos:
                continue
            if max(abs(ox - tx), abs(oy - ty)) == 1:
                # Check obstacle is roughly between attacker and target
                if (ax - tx) * (ox - tx) + (ay - ty) * (oy - ty) > 0:
                    best = max(best, 5)
        for ox, oy in self.trees:
            if (ox, oy) == target_pos:
                continue
            if max(abs(ox - tx), abs(oy - ty)) == 1:
                if (ax - tx) * (ox - tx) + (ay - ty) * (oy - ty) > 0:
                    best = max(best, 2)
        return best

    def _is_obscured_between(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
        """Return True if a tree or rock lies between two cells (excluding endpoints)."""
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0

        while (x, y) != (x1, y1):
            if (x, y) not in (start, end) and (x, y) in (self.trees | self.rocks):
                return True
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return False

    def _enemy_sight_range_cells(self, enemy: Character) -> int:
        move_cells = max(1, int(max(0, getattr(enemy, "speed_ft", 30)) // 5))
        darkvision_ft = int(getattr(enemy, "darkvision_range", 0) or 0)
        darkvision_cells = max(0, darkvision_ft // 5)
        return max(move_cells, darkvision_cells)

    def _enemy_passive_perception(self, enemy: Character) -> int:
        explicit = getattr(enemy, "passive_perception", None)
        if isinstance(explicit, (int, float)):
            return int(explicit)
        perception_bonus = getattr(enemy, "perception_bonus", None)
        if isinstance(perception_bonus, (int, float)):
            return 10 + int(perception_bonus)
        return 10

    def _player_stealth_bonus(self) -> int:
        return self.player.get_skill_bonus("Stealth")

    def _enemy_can_attempt_detection(self, enemy: Character, enemy_pos: tuple[int, int]) -> bool:
        distance = max(abs(enemy_pos[0] - self.player_pos[0]), abs(enemy_pos[1] - self.player_pos[1]))
        if distance > self._enemy_sight_range_cells(enemy):
            return False
        if self._is_obscured_between(enemy_pos, self.player_pos):
            return False
        return True

    def attempt_hide(self) -> tuple[bool, str]:
        """Attempt to hide using Stealth vs visible enemies' passive Perception."""
        stealth_roll = self.player.roll_d20()
        stealth_total = stealth_roll + self._player_stealth_bonus()

        observers = []
        for enemy in self.enemies:
            if not enemy.is_alive() or enemy not in self.enemy_positions:
                continue
            enemy_pos = self.enemy_positions[enemy]
            if not self._enemy_can_attempt_detection(enemy, enemy_pos):
                continue
            observers.append((enemy, self._enemy_passive_perception(enemy)))

        if not observers:
            self.hidden = True
            self.hidden_stealth_total = stealth_total
            return True, f"Hide: no enemy has clear sight. Stealth {stealth_total}."

        spotted_by = [enemy.name for enemy, passive in observers if stealth_total <= passive]
        if spotted_by:
            self.hidden = False
            self.hidden_stealth_total = None
            return False, f"Hide failed (Stealth {stealth_total}): spotted by {', '.join(spotted_by)}."

        self.hidden = True
        self.hidden_stealth_total = stealth_total
        return True, f"Hide successful (Stealth {stealth_total}) against {len(observers)} observer(s)."

    def _reveal_player_from_hidden(self, source: str = "action") -> None:
        if not self.hidden:
            return
        self.hidden = False
        self.hidden_stealth_total = None
        if source == "attack":
            self.add_log("You attack from hiding, revealing your position!")
        elif source == "spell":
            self.add_log("You cast from hiding, revealing your position!")
        else:
            self.add_log("You reveal your position.")

    # ------------------------------------------------------------------
    # Enemy stealth helpers
    # ------------------------------------------------------------------

    def _enemy_stealth_total(self, enemy: Character) -> int:
        """Roll a Stealth check for an enemy (d20 + stealth bonus)."""
        roll = random.randint(1, 20)
        bonus = int(getattr(enemy, "stealth_bonus", 0))
        return roll + bonus

    def _player_passive_perception(self) -> int:
        """Return the player's passive Perception (10 + Perception bonus)."""
        return 10 + self.player.get_skill_bonus("Perception")

    def _player_can_attempt_detection(self, enemy: Character) -> bool:
        """Return True if the player can attempt to spot a hidden enemy (in range + line of sight)."""
        if enemy not in self.enemy_positions:
            return False
        ex, ey = self.enemy_positions[enemy]
        px, py = self.player_pos
        distance = max(abs(ex - px), abs(ey - py))
        # Player can attempt detection within their vision range (max of darkvision or 6 cells)
        darkvision_ft = int(getattr(self.player, "darkvision_range", 0) or 0)
        vision = max(6, darkvision_ft // 5)
        if distance > vision:
            return False
        if self._is_obscured_between(self.player_pos, (ex, ey)):
            return False
        return True

    def _check_player_perception_vs_hidden_enemies(self) -> None:
        """At the start of the player's turn, roll an active Perception
        check against each hidden enemy in range. Only log when the
        player succeeds; failed checks are completely silent so the
        player doesn't know there's a hidden enemy nearby.
        """
        revealed = []
        for enemy in list(self.hidden_enemies):
            if not enemy.is_alive():
                self.hidden_enemies.discard(enemy)
                continue
            if not self._player_can_attempt_detection(enemy):
                continue
            stealth_total = getattr(enemy, "_stealth_check_total", None)
            if stealth_total is None:
                # Enemy hasn't rolled yet — use their bonus + 10 (take-10)
                stealth_total = 10 + int(getattr(enemy, "stealth_bonus", 0))
            # Active Perception roll: d20 + Perception bonus
            perception_roll = self.player.roll_d20() + self.player.get_skill_bonus("Perception")
            if perception_roll >= stealth_total:
                revealed.append((enemy, perception_roll))
        for enemy, roll in revealed:
            self.hidden_enemies.discard(enemy)
            self.add_log(f"You spot {enemy.name} lurking in the shadows! (Perception {roll})")

    def _reveal_enemy_from_hidden(self, enemy: Character) -> None:
        """Reveal a hidden enemy (e.g. when it attacks)."""
        self.hidden_enemies.discard(enemy)

    def _enemy_attempt_re_stealth(self, enemy: Character) -> None:
        """After attacking, a sneaky enemy tries to vanish again if obscured."""
        if getattr(enemy, "behavior", "") != "sneaky":
            return
        if enemy not in self.enemy_positions:
            return
        ex, ey = self.enemy_positions[enemy]
        px, py = self.player_pos
        # Can only re-stealth if obscured from the player (behind cover)
        if not self._is_obscured_between((ex, ey), (px, py)):
            return
        stealth_total = self._enemy_stealth_total(enemy)
        # Player rolls active Perception to contest the re-stealth
        perception_roll = self.player.roll_d20() + self.player.get_skill_bonus("Perception")
        if stealth_total > perception_roll:
            enemy._stealth_check_total = stealth_total
            self.hidden_enemies.add(enemy)
            # Don't tell the player the enemy re-stealthed — they just vanish
        else:
            self.add_log(f"{enemy.name} tries to slip into the shadows but you keep track of it.")

    def add_log(self, text: str) -> None:
        if not text:
            return
        self.combat_log.append(text)
        if len(self.combat_log) > 200:
            self.combat_log = self.combat_log[-200:]

    def can_use_action(self) -> bool:
        return self.actions_remaining > 0

    def can_use_cunning_action(self) -> bool:
        class_key = str(getattr(self.player, "class_name", "") or "").strip().lower()
        return class_key == "rogue" and int(getattr(self.player, "level", 1)) >= 2 and not self.spent_bonus_action

    def spend_action_or_cunning_bonus(self) -> str | None:
        if self.can_use_action():
            self.spend_action()
            return "action"
        if self.can_use_cunning_action():
            self.spent_bonus_action = True
            return "bonus"
        return None

    def spend_action(self) -> bool:
        if self.actions_remaining <= 0:
            self.spent_action = True
            return False
        self.actions_remaining -= 1
        self.spent_action = self.actions_remaining <= 0
        return True

    def gain_action(self, amount: int = 1) -> None:
        if amount <= 0:
            return
        self.actions_remaining += amount
        self.spent_action = self.actions_remaining <= 0

    # ------------------------------------------------------------------
    # Trigger queue: mid-combat confirmation popups
    # ------------------------------------------------------------------

    def queue_trigger(self, trigger: dict) -> None:
        """Add a trigger to the pending confirmation queue.

        A trigger dict should contain:
          title: str           - Modal title (e.g. "Attack of Opportunity")
          description: list[str] - Lines of explanatory text
          accept_label: str    - Label for the "Yes" button
          decline_label: str   - Label for the "No" button
          on_accept: callable  - Called (no args) when the player accepts
          on_decline: callable - Called (no args) when the player declines (optional)
        """
        self.pending_triggers.append(trigger)

    def get_current_trigger_modal(self) -> dict | None:
        """Return a modal dict for the current pending trigger, or ``None``."""
        if not self.pending_triggers:
            return None
        t = self.pending_triggers[0]
        return {
            "title": t.get("title", "Reaction"),
            "lines": t.get("description", []),
            "buttons": [
                ("trigger_accept", t.get("accept_label", "Yes")),
                ("trigger_decline", t.get("decline_label", "No")),
            ],
        }

    def resolve_current_trigger(self, accepted: bool) -> None:
        """Resolve the front trigger and pop it from the queue."""
        if not self.pending_triggers:
            return
        trigger = self.pending_triggers.pop(0)
        if accepted:
            callback = trigger.get("on_accept")
            if callback:
                callback()
        else:
            callback = trigger.get("on_decline")
            if callback:
                callback()

    def _get_player_melee_reach(self) -> int:
        """Return the player's melee reach in grid tiles (1 = 5 ft, 2 = 10 ft Reach)."""
        weapon = self.player.equipped_weapon
        if weapon:
            from items import Weapon
            if isinstance(weapon, Weapon):
                prof = getattr(weapon, "proficiency_type", "")
                if "Ranged" in prof:
                    return 1  # Ranged weapon, fall back to unarmed reach
                if weapon.has_property("Reach"):
                    return 2
        return 1

    def _player_has_melee_capability(self) -> bool:
        """Return True if the player can make a melee opportunity attack."""
        weapon = self.player.equipped_weapon
        if weapon:
            from items import Weapon
            if isinstance(weapon, Weapon):
                prof = getattr(weapon, "proficiency_type", "")
                if "Ranged" in prof:
                    return False  # Pure ranged weapon, no melee AoO
        return True

    def _check_aoo_triggers(self, pre_move_positions: dict) -> None:
        """Queue Attack of Opportunity triggers for enemies that left melee reach.

        Called after ``move_enemies()`` with the enemy positions from *before*
        movement.  If the player hasn't used their reaction and an enemy
        moved from within reach to outside reach, an AoO trigger is queued.
        """
        if self.reaction_used:
            return
        if not self._player_has_melee_capability():
            return
        if not self.player.is_alive():
            return

        reach = self._get_player_melee_reach()
        px, py = self.player_pos

        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            old_pos = pre_move_positions.get(enemy)
            new_pos = self.enemy_positions.get(enemy)
            if old_pos is None or new_pos is None:
                continue
            if old_pos == new_pos:
                continue  # Didn't move

            old_dist = max(abs(old_pos[0] - px), abs(old_pos[1] - py))
            new_dist = max(abs(new_pos[0] - px), abs(new_pos[1] - py))

            if old_dist <= reach and new_dist > reach:
                # This enemy left our reach – offer AoO
                # Capture enemy in closure
                _enemy = enemy
                def _make_aoo_accept(e=_enemy):
                    def _accept():
                        self.reaction_used = True
                        # Make a melee attack against the fleeing enemy
                        result = self.player.attack(e, log_fn=self.add_log, target_distance=1)
                        hit = "-> HIT" in result
                        if not e.is_alive():
                            gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(e)
                            self.add_log(f"Opportunity Attack slays {e.name}! Looted {gold_gain} gold.")
                            if item_drop:
                                self.add_log(f"{e.name} dropped {item_drop}.")
                        elif hit:
                            self.add_log(f"Opportunity Attack hits {e.name}!")
                        else:
                            self.add_log(f"Opportunity Attack misses {e.name}.")
                    return _accept

                self.queue_trigger({
                    "title": "Attack of Opportunity",
                    "description": [
                        f"{enemy.name} is leaving your reach!",
                        "",
                        "Spend your reaction to make a melee attack",
                        "against this creature as it moves away?",
                        "",
                        f"(You have {'' if not self.reaction_used else 'no '}1 reaction this round)",
                    ],
                    "accept_label": "Attack!",
                    "decline_label": "Let them go",
                    "on_accept": _make_aoo_accept(),
                    "on_decline": None,
                })
                # Only one AoO per round (reaction economy)
                break

    def _queue_weapon_mastery_trigger(self, enemy: Character, mastery: str) -> None:
        """Queue a confirmation trigger for optional weapon masteries (Push/Cleave/Nick)."""
        mastery_lower = mastery.strip().lower()

        if mastery_lower == "push":
            self.queue_trigger({
                "title": "Weapon Mastery: Push",
                "description": [
                    f"Your attack hit {enemy.name}!",
                    "",
                    "Push: Shove the target 1 tile away from you.",
                    "Activate this weapon mastery?",
                ],
                "accept_label": "Push!",
                "decline_label": "Skip",
                "on_accept": lambda: self._apply_push_mastery(enemy),
                "on_decline": None,
            })
        elif mastery_lower == "cleave":
            if self.cleave_used_this_turn:
                return
            # Check if there are adjacent secondary targets first
            if enemy not in self.enemy_positions:
                return
            target_pos = self.enemy_positions[enemy]
            candidates = []
            for other, pos in self.enemy_positions.items():
                if other is enemy or not other.is_alive():
                    continue
                if max(abs(pos[0] - target_pos[0]), abs(pos[1] - target_pos[1])) > 1:
                    continue
                if max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1])) > self.player.get_attack_range():
                    continue
                candidates.append(other)
            if not candidates:
                return
            target_names = ", ".join(c.name for c in candidates[:3])
            self.queue_trigger({
                "title": "Weapon Mastery: Cleave",
                "description": [
                    f"Your attack hit {enemy.name}!",
                    "",
                    f"Cleave: Deal weapon damage to an adjacent enemy.",
                    f"Nearby targets: {target_names}",
                    "Activate this weapon mastery?",
                ],
                "accept_label": "Cleave!",
                "decline_label": "Skip",
                "on_accept": lambda: self._apply_cleave_mastery(primary_target=enemy),
                "on_decline": None,
            })
        elif mastery_lower == "nick":
            if self.nick_used_this_turn:
                return
            offhand = self.player.equipped_offhand
            from items import Weapon
            if not isinstance(offhand, Weapon) or not offhand.has_property("Light"):
                return
            self.queue_trigger({
                "title": "Weapon Mastery: Nick",
                "description": [
                    f"Your attack hit {enemy.name}!",
                    "",
                    "Nick: Make an extra offhand attack with your",
                    f"light weapon ({offhand.name}).",
                    "Activate this weapon mastery?",
                ],
                "accept_label": "Strike!",
                "decline_label": "Skip",
                "on_accept": lambda: self._apply_nick_mastery(primary_target=enemy),
                "on_decline": None,
            })

    def _queue_on_hit_species_triggers(self, enemy: Character) -> None:
        """Queue triggers for optional on-hit species features (e.g. Goliath ancestry)."""
        options = self.player.get_on_hit_feature_options(enemy)
        for option in options:
            feature_id = str(option.get("id", "")).strip()
            if not feature_id:
                continue
            label = str(option.get("label", feature_id))
            description = str(option.get("description", "Activate on-hit feature"))

            # Capture in closure
            _fid = feature_id
            _enemy = enemy
            self.queue_trigger({
                "title": f"On-Hit: {label}",
                "description": [
                    f"Your attack hit {enemy.name}!",
                    "",
                    description,
                    "",
                    "Activate this feature?",
                ],
                "accept_label": "Activate!",
                "decline_label": "Skip",
                "on_accept": lambda fid=_fid, e=_enemy: self.player.activate_on_hit_feature(fid, e, log_fn=self.add_log),
                "on_decline": None,
            })

    def move_player(self, target_x: int, target_y: int) -> bool:
        """Move player to target position on grid. Return True if moved."""
        # Clamp to grid bounds
        target_x = max(0, min(GRID_WIDTH - 1, target_x))
        target_y = max(0, min(GRID_HEIGHT - 1, target_y))

        if (target_x, target_y) in self.obstacles:
            self.message = "That tile is blocked."
            self.message_timer = 30
            return False

        distance = max(abs(target_x - self.player_pos[0]), abs(target_y - self.player_pos[1]))
        if distance == 0:
            return False
        remaining = max(0, self.movement_max - self.movement_used)
        if distance > remaining:
            self.message = "Not enough movement remaining."
            self.message_timer = 30
            return False

        self.player_pos = (target_x, target_y)
        self.movement_used += distance
        self.compute_player_visibility()
        self.message = f"Moved {distance} spaces."
        self.message_timer = 20
        return True

    def attack_enemy_at(self, target_pos: tuple[int, int]) -> bool:
        """Attack an enemy at the target position. Return True if an attack occurred."""
        # Fog of war: can't target what you can't see
        if not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False

        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue
            # Can't target enemies hidden by stealth
            if enemy in self.hidden_enemies:
                continue
            
            # If hidden, reveal position on attack
            self._reveal_player_from_hidden(source="attack")
            self.last_known_player_pos = self.player_pos
            
            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > self.player.attack_range:
                self.message = "Target out of range."
                self.message_timer = 40
                return False
            if self.player.attack_range > 1 and not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False
            cover_bonus = self._cover_bonus(self.player_pos, pos) if self.player.attack_range > 1 else 0
            original_cover = enemy.temp_ac_bonus
            enemy.temp_ac_bonus += cover_bonus
            attack_result = self.player.attack(enemy, log_fn=self.add_log, target_distance=distance)
            enemy.temp_ac_bonus = original_cover

            hit = "-> HIT" in attack_result or "Graze deals" in attack_result
            strict_hit = "-> HIT" in attack_result
            mastery = self.player.get_weapon_mastery().strip().lower()

            # Clear old on-hit action buttons (replaced by trigger queue)
            self.pending_on_hit_actions = {}

            # Queue optional weapon mastery triggers (Push/Cleave/Nick)
            if hit and enemy.is_alive() and mastery in ("push", "cleave", "nick"):
                self._queue_weapon_mastery_trigger(enemy, mastery)

            # Queue optional on-hit species feature triggers (Goliath ancestry, etc.)
            if strict_hit and enemy.is_alive():
                self._queue_on_hit_species_triggers(enemy)

            if not enemy.is_alive():
                gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(enemy)
                self.message = f"Defeated {enemy.name}! Looted {gold_gain} gold."
                self.message_timer = 40
                self.add_log(self.message)
                if item_drop:
                    self.add_log(f"{enemy.name} dropped {item_drop}.")
                # Clear triggers if target died
                self.pending_triggers = []
            else:
                if hit:
                    self.message = f"Hit {enemy.name}!"
                else:
                    self.message = f"Missed {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)
            self.spend_action()
            # If triggers were queued (weapon mastery / on-hit), enter trigger phase
            if self.pending_triggers:
                self._trigger_resume_phase = "player_input"
                self.turn_phase = "awaiting_trigger"
            return True
        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def _set_pending_on_hit_options(self, target: Character) -> None:
        self.pending_on_hit_actions = {}
        options = self.player.get_on_hit_feature_options(target)
        for option in options:
            feature_id = str(option.get("id", "")).strip()
            if not feature_id:
                continue
            action_id = f"on_hit::{feature_id}"
            self.pending_on_hit_actions[action_id] = {
                "feature_id": feature_id,
                "target": target,
                "label": str(option.get("label", feature_id)),
                "description": str(option.get("description", "")),
            }

    def get_pending_on_hit_ui_actions(self) -> tuple[list[tuple[str, str, bool, str]], dict[str, str]]:
        actions: list[tuple[str, str, bool, str]] = []
        tooltips: dict[str, str] = {}
        for action_id, data in self.pending_on_hit_actions.items():
            target = data.get("target")
            if target is None or not target.is_alive():
                continue
            label = str(data.get("label", "On-Hit Feature"))
            actions.append((label, action_id, False, ""))
            tooltip = str(data.get("description", "Activate optional on-hit feature"))
            tooltips[action_id] = tooltip
        return actions, tooltips

    def activate_pending_on_hit_action(self, action_id: str) -> bool:
        entry = self.pending_on_hit_actions.get(action_id)
        if not entry:
            self.message = "That on-hit option is no longer available."
            self.message_timer = 30
            return False
        target = entry.get("target")
        if target is None or not target.is_alive():
            self.pending_on_hit_actions = {}
            self.message = "Target is no longer valid for on-hit feature."
            self.message_timer = 30
            return False

        feature_id = str(entry.get("feature_id", ""))
        result = self.player.activate_on_hit_feature(feature_id, target, log_fn=self.add_log)
        self.message = result
        self.message_timer = 40
        self.pending_on_hit_actions = {}
        return True

    def breath_weapon_enemy_at(self, target_pos: tuple[int, int]) -> bool:
        """Use Dragonborn Breath Weapon on an enemy at target position."""
        if not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False
        if not self.player.can_use_breath_weapon():
            self.message = "Breath Weapon not available."
            self.message_timer = 40
            return False

        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > 3:
                self.message = "Target out of breath range."
                self.message_timer = 40
                return False
            if not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False

            self.player.use_breath_weapon(enemy, log_fn=self.add_log)
            if not enemy.is_alive():
                gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(enemy)
                self.message = f"Breath Weapon defeated {enemy.name}! Looted {gold_gain} gold."
                self.message_timer = 40
                self.add_log(self.message)
                if item_drop:
                    self.add_log(f"{enemy.name} dropped {item_drop}.")
            else:
                self.message = f"Breath Weapon hit {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)

            self.spend_action()
            return True

        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def species_magic_enemy_at(self, target_pos: tuple[int, int]) -> bool:
        """Use species lineage/legacy magic on one enemy at target position."""
        if not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False
        if not self.player.has_species_magic():
            self.message = "Species magic not available."
            self.message_timer = 40
            return False

        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > self.player.get_species_magic_range():
                self.message = "Target out of species magic range."
                self.message_timer = 40
                return False
            if self.player.get_species_magic_range() > 1 and not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False

            self.player.use_species_magic(enemy, log_fn=self.add_log)
            if not enemy.is_alive():
                gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(enemy)
                self.message = f"{self.player.get_species_magic_label()} defeated {enemy.name}! Looted {gold_gain} gold."
                self.message_timer = 40
                self.add_log(self.message)
                if item_drop:
                    self.add_log(f"{enemy.name} dropped {item_drop}.")
            else:
                self.message = f"{self.player.get_species_magic_label()} hit {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)

            self.spend_action()
            return True

        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def cast_spell_at(self, spell_name: str, target_pos: tuple[int, int]) -> bool:
        """Cast a known spell at an enemy located at target position."""
        if not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False
        if not self.player.can_cast_spell(spell_name):
            self.message = f"Cannot cast {spell_name} right now."
            self.message_timer = 40
            return False

        spell_range = self.player.get_spell_range(spell_name)
        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue
            # Can't target enemies hidden by stealth
            if enemy in self.hidden_enemies:
                continue

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > spell_range:
                self.message = "Target out of spell range."
                self.message_timer = 40
                return False
            if spell_range > 1 and not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False

            # Apply cover bonus for ranged spell attacks (SRD 5.2.1)
            spell_cover = self._cover_bonus(self.player_pos, pos) if distance > 1 else 0
            original_cover = enemy.temp_ac_bonus
            enemy.temp_ac_bonus += spell_cover

            self._reveal_player_from_hidden(source="spell")
            result = self.player.cast_spell(spell_name, target=enemy, log_fn=self.add_log)
            enemy.temp_ac_bonus = original_cover
            if not enemy.is_alive():
                gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(enemy)
                self.message = f"{spell_name} defeated {enemy.name}! Looted {gold_gain} gold."
                self.message_timer = 40
                self.add_log(self.message)
                if item_drop:
                    self.add_log(f"{enemy.name} dropped {item_drop}.")
            elif "MISS" in result:
                self.message = f"{spell_name} missed {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)
            else:
                self.message = f"{spell_name} hits {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)

            self.spend_action()
            return True

        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def apply_hunters_mark_at(self, target_pos: tuple[int, int]) -> bool:
        """Apply Hunter's Mark to an enemy at target position."""
        if not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False
        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > 6:
                self.message = "Hunter's Mark range is 30 ft (6 tiles)."
                self.message_timer = 40
                return False
            if distance > 1 and not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False

            if not self.player.use_hunters_mark(enemy):
                self.message = "Hunter's Mark not available."
                self.message_timer = 40
                return False

            self.spent_bonus_action = True
            self.message = f"Hunter's Mark applied to {enemy.name}."
            self.message_timer = 40
            self.add_log(self.message)
            return True

        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def apply_martial_arts_strike_at(self, target_pos: tuple[int, int]) -> bool:
        """Perform a Martial Arts bonus unarmed strike against enemy at *target_pos*."""
        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > 1:
                self.message = "Unarmed Strike: must be adjacent (melee range)."
                self.message_timer = 40
                return False

            result = self.player.martial_arts_strike(enemy, log_fn=self.add_log)
            self.spent_bonus_action = True
            self.message = result
            self.message_timer = 60

            if not enemy.is_alive():
                gold_gain, _, item_drop = self._apply_enemy_defeat_rewards(enemy)
                self.message = f"Defeated {enemy.name}! Looted {gold_gain} gold."
                self.message_timer = 40
                self.add_log(self.message)
                if item_drop:
                    self.add_log(f"{enemy.name} dropped {item_drop}.")

            return True

        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def _spell_target_in_range(self, spell_name: str, target_pos: tuple[int, int]) -> bool:
        aoe = self.player.get_spell_aoe(spell_name)
        if aoe and aoe.get("shape") == "burst_self":
            return True
        spell_range = self.player.get_spell_range(spell_name)
        distance = max(abs(target_pos[0] - self.player_pos[0]), abs(target_pos[1] - self.player_pos[1]))
        if distance > spell_range:
            return False
        if spell_range > 1 and not self._has_line_of_sight(self.player_pos, target_pos):
            return False
        return True

    def get_spell_aoe_cells(self, spell_name: str, target_pos: tuple[int, int]) -> set[tuple[int, int]]:
        aoe = self.player.get_spell_aoe(spell_name)
        if not aoe:
            return set()
        shape = aoe.get("shape", "radius")
        px, py = self.player_pos
        cells = set()
        if shape == "burst_self":
            radius = int(aoe.get("radius", 1))
            for x in range(px - radius, px + radius + 1):
                for y in range(py - radius, py + radius + 1):
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        if max(abs(x - px), abs(y - py)) <= radius:
                            cells.add((x, y))
            return cells

        tx, ty = target_pos
        if shape == "radius":
            radius = int(aoe.get("radius", 1))
            for x in range(tx - radius, tx + radius + 1):
                for y in range(ty - radius, ty + radius + 1):
                    if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                        if max(abs(x - tx), abs(y - ty)) <= radius:
                            cells.add((x, y))
            return cells

        if shape == "cone":
            length = int(aoe.get("length", 3))
            dx = tx - px
            dy = ty - py
            if dx == 0 and dy == 0:
                return set()
            mag = math.sqrt(dx * dx + dy * dy)
            if mag <= 0:
                return set()
            dir_x = dx / mag
            dir_y = dy / mag

            for x in range(px - length, px + length + 1):
                for y in range(py - length, py + length + 1):
                    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                        continue
                    vx = x - px
                    vy = y - py
                    dist = max(abs(vx), abs(vy))
                    if dist == 0 or dist > length:
                        continue
                    vmag = math.sqrt(vx * vx + vy * vy)
                    if vmag <= 0:
                        continue
                    cos_theta = (vx * dir_x + vy * dir_y) / vmag
                    # 90-degree cone (45 degrees to either side)
                    if cos_theta >= 0.707:
                        cells.add((x, y))
        return cells

    def cast_aoe_spell_at(self, spell_name: str, target_pos: tuple[int, int]) -> bool:
        # Self-centred AoE spells (e.g. Thunderwave) bypass the visibility check
        aoe_info = self.player.get_spell_aoe(spell_name)
        is_self_aoe = aoe_info and aoe_info.get("shape") == "burst_self"
        if not is_self_aoe and not self.is_cell_visible(*target_pos):
            self.message = "You can't see that area."
            self.message_timer = 40
            return False
        if not self.player.can_cast_spell(spell_name):
            self.message = f"Cannot cast {spell_name} right now."
            self.message_timer = 40
            return False
        if not self._spell_target_in_range(spell_name, target_pos):
            self.message = "Target out of spell range or line of sight blocked."
            self.message_timer = 40
            return False

        aoe_cells = self.get_spell_aoe_cells(spell_name, target_pos)
        targets = [enemy for enemy, pos in self.enemy_positions.items()
                   if enemy.is_alive() and pos in aoe_cells]

        # AoE hits reveal any hidden enemies caught in the blast
        for enemy in targets:
            if enemy in self.hidden_enemies:
                self._reveal_enemy_from_hidden(enemy)
                self.add_log(f"{enemy.name} is flushed out of hiding by the blast!")

        self._reveal_player_from_hidden(source="spell")
        self.player.cast_aoe_spell(spell_name, targets, log_fn=self.add_log)
        defeated = []
        for enemy in targets:
            if not enemy.is_alive():
                defeated.append(enemy)

        total_bounty = 0
        total_xp = 0
        drop_count = 0
        for enemy in defeated:
            gold_gain, xp_gain, item_drop = self._apply_enemy_defeat_rewards(enemy)
            total_bounty += gold_gain
            total_xp += xp_gain
            if item_drop:
                drop_count += 1

        if total_bounty > 0:
            self.message = f"{spell_name} defeated {len(defeated)} enemy(s)! Looted {total_bounty} gold."
            self.message_timer = 40
            self.add_log(self.message)
            if drop_count > 0:
                self.add_log(f"Found {drop_count} item drop(s).")
        else:
            self.message = f"{spell_name} resolves."
            self.message_timer = 30

        self.spend_action()
        return True
    
    def move_enemies(self):
        """Move enemies toward the player/last-known position using speed in tiles.

        Behavior priority:
        1) Pursue visible player position
        2) If hidden, pursue last known player position
        3) Fallback to keep gate when no valid last-known target
        """
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            if enemy not in self.enemy_positions:
                continue

            target_x, target_y = self.player_pos
            if self.hidden:
                if self.last_known_player_pos is not None:
                    target_x, target_y = self.last_known_player_pos
                    if self.enemy_positions[enemy] == self.last_known_player_pos:
                        target_x, target_y = GATE_X, GATE_Y
                else:
                    target_x, target_y = GATE_X, GATE_Y
            else:
                self.last_known_player_pos = self.player_pos

            move_tiles = max(1, enemy.get_speed_ft() // 5)
            for _ in range(move_tiles):
                ex, ey = self.enemy_positions[enemy]
                dx = target_x - ex
                dy = target_y - ey
                distance = max(abs(dx), abs(dy))

                if distance <= enemy.attack_range:
                    break

                step_x = 1 if dx > 0 else -1 if dx < 0 else 0
                step_y = 1 if dy > 0 else -1 if dy < 0 else 0

                candidates = [
                    (ex + step_x, ey + step_y),
                    (ex + step_x, ey),
                    (ex, ey + step_y),
                ]

                occupied_tiles = {
                    pos for other, pos in self.enemy_positions.items()
                    if other is not enemy and other.is_alive()
                }

                moved = False
                for nx, ny in candidates:
                    if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                        continue
                    if (nx, ny) == self.player_pos:
                        continue
                    if (nx, ny) in self.rocks:
                        continue
                    if (nx, ny) in occupied_tiles:
                        continue
                    self.enemy_positions[enemy] = (nx, ny)
                    moved = True
                    break

                if not moved:
                    break
    
    def _resolve_single_enemy(self, enemy: Character) -> bool:
        """Process a single enemy's turn. Return True if the player died."""
        px, py = self.player_pos

        if not enemy.is_alive():
            return False

        if getattr(enemy, "behavior", "") == "regenerator" and enemy.hp < enemy.max_hp:
            healed = enemy.heal(2)
            if healed > 0:
                self.add_log(f"{enemy.name} regenerates {healed} HP.")

        if enemy not in self.enemy_positions:
            return False

        ex, ey = self.enemy_positions[enemy]

        distance = max(abs(ex - px), abs(ey - py))

        if self.hidden:
            if self.hidden_stealth_total is None:
                self.hidden = False
            elif self._enemy_can_attempt_detection(enemy, (ex, ey)):
                passive = self._enemy_passive_perception(enemy)
                if self.hidden_stealth_total <= passive:
                    self.hidden = False
                    self.hidden_stealth_total = None
                    self.last_known_player_pos = (px, py)
                    self.add_log(f"{enemy.name} spots you (Passive Perception {passive}).")
                else:
                    return False
            else:
                return False

        # Update last known position if in range and can see
        if distance <= enemy.attack_range or distance <= 3:  # Liberal vision range
            self.last_known_player_pos = (px, py)

        if getattr(enemy, "behavior", "") == "healer" and enemy.potions > 0:
            wounded = [ally for ally in self.enemies if ally.is_alive() and ally is not enemy and ally.hp < ally.max_hp]
            if wounded:
                target = min(wounded, key=lambda ally: ally.hp)
                healed = enemy.heal_ally(target, 7)
                if healed > 0:
                    self.add_log(f"{enemy.name} heals {target.name} for {healed} HP.")
                    return False

        if enemy.is_alive() and distance <= enemy.attack_range:
            # Sneaky enemy attacking from stealth: grant advantage + bonus damage
            is_sneaking = enemy in self.hidden_enemies
            if is_sneaking:
                enemy._stealth_advantage = True
                self._reveal_enemy_from_hidden(enemy)
                self.add_log(f"{enemy.name} strikes from the shadows!")
            # Apply cover bonus to player when attacked at range (SRD 5.2.1)
            if distance > 1:
                player_cover = self._cover_bonus((ex, ey), self.player_pos)
                self.player.temp_ac_bonus += player_cover
            else:
                player_cover = 0
            attack_result = enemy.attack(self.player, log_fn=self.add_log, target_distance=distance)
            if player_cover:
                self.player.temp_ac_bonus -= player_cover
            # Sneaky enemy sneak attack bonus damage on hit
            if is_sneaking and "-> HIT" in attack_result and self.player.is_alive():
                sneak_dice = int(getattr(enemy, "sneak_attack_dice", 1))
                sneak_dmg = sum(random.randint(1, 6) for _ in range(sneak_dice))
                if hasattr(self.player, "take_damage"):
                    sneak_dmg, _ = self.player.take_damage(sneak_dmg, damage_type="physical", source=enemy, log_fn=self.add_log)
                else:
                    self.player.hp -= sneak_dmg
                self.add_log(f"{enemy.name} deals {sneak_dmg} sneak attack damage! ({sneak_dice}d6)")
            if getattr(enemy, "behavior", "") == "mage" and "-> HIT" in attack_result and self.player.is_alive():
                if random.random() < 0.35:
                    self.player.apply_status_effect("poisoned", rounds=2, potency=2)
                    self.add_log(f"{enemy.name} inflicts Poisoned on {self.player.name} (2 rounds).")
            if not self.player.is_alive():
                self.message = "You have been slain!"
                self.message_timer = 60
                self.add_log(self.message)
                return True
            # After attacking, sneaky enemy tries to re-stealth if behind cover
            if is_sneaking:
                self._enemy_attempt_re_stealth(enemy)
        return False

    def resolve_combat(self):
        """Enemy attacks if in range and can see player."""
        for enemy in self.enemies:
            self._resolve_single_enemy(enemy)
    
    def update(self, window: GameWindow):
        """Update game state each frame."""
        if self.pause_frames > 0:
            self.pause_frames -= 1
            if self.message_timer > 0:
                self.message_timer -= 1
            return

        if self.turn_phase == "awaiting_trigger":
            # Waiting for the player to respond to a trigger modal.
            # Input is handled in the main loop; nothing to do here.
            return
        
        if self.turn_phase == "player_input":
            if not self.player_turn_started:
                self.player.start_turn()
                # Dodge / defend AC bonus expires "at start of your next turn" (SRD)
                self.player.temp_ac_bonus = 0
                self.movement_max = max(1, self.player.get_speed_ft() // 5)
                self.movement_used = 0
                self.actions_remaining = 1
                self.spent_action = False
                self.spent_bonus_action = False
                self.sneak_attack_used_this_turn = False
                self.spell_menu_open = False
                self.player_turn_started = True
                self.cleave_used_this_turn = False
                self.nick_used_this_turn = False
                self.reaction_used = False  # Reaction resets at start of turn
                # Passive Perception check vs hidden enemies at start of turn
                self._check_player_perception_vs_hidden_enemies()
            self.message = ">>> Your turn! Click to move or take an action <<<"
            self.message_timer = 999
            # Waiting for player input (handled in main loop)
            return
        
        if self.turn_phase == "processing":
            if self._processing_subphase == "idle":
                # Step 1: Snapshot enemy positions BEFORE movement
                pre_move_positions = {
                    e: pos for e, pos in self.enemy_positions.items()
                    if e.is_alive()
                }

                # Step 2: Move enemies
                self.move_enemies()
                self.pause_frames = 30  # Show movement for 0.5 seconds

                # Step 3: Check for Attack of Opportunity triggers
                self._check_aoo_triggers(pre_move_positions)
                if self.pending_triggers:
                    self._trigger_resume_phase = "processing"
                    self._processing_subphase = "post_movement"
                    self.turn_phase = "awaiting_trigger"
                    return

                self._processing_subphase = "post_movement"
                # Fall through to resolve combat

            if self._processing_subphase == "post_movement":
                # Start stepping through enemies one at a time
                self._enemy_turn_index = 0
                self._processing_subphase = "resolving_enemies"
                # Fall through to resolving_enemies

            if self._processing_subphase == "resolving_enemies":
                # Process one enemy per step, with a pause between each
                alive_enemies = [e for e in self.enemies if e.is_alive()]
                if self._enemy_turn_index < len(alive_enemies):
                    enemy = alive_enemies[self._enemy_turn_index]
                    player_died = self._resolve_single_enemy(enemy)
                    self._enemy_turn_index += 1
                    if player_died:
                        # Player died – skip remaining enemies
                        self._processing_subphase = "cleanup"
                    elif self._enemy_turn_index < len(alive_enemies):
                        # More enemies to go – pause so the player can read the log
                        self.pause_frames = 90  # 1.5 seconds at 60 FPS
                        return
                    else:
                        # All enemies done
                        self._processing_subphase = "cleanup"
                else:
                    self._processing_subphase = "cleanup"

            if self._processing_subphase == "cleanup":
                for message in self.player.end_round():
                    self.message = message
                    self.message_timer = 40

                # Clean up dead enemies from hidden set
                self.hidden_enemies = {e for e in self.hidden_enemies if e.is_alive()}

                # Reset and switch back to player input
                self._processing_subphase = "idle"
                self._enemy_turn_index = 0
                self.turn_phase = "player_input"
                self.pause_frames = 30
                self.targeting_mode = False
                self.targeting_action = None
                self.movement_used = 0
                self.player_turn_started = False
                self.cleave_used_this_turn = False
                self.nick_used_this_turn = False
                self.pending_on_hit_actions = {}
        
        if self.message_timer > 0:
            self.message_timer -= 1

    def _apply_push_mastery(self, enemy: Character) -> None:
        if enemy not in self.enemy_positions:
            return
        ex, ey = self.enemy_positions[enemy]
        px, py = self.player_pos
        step_x = 1 if ex > px else -1 if ex < px else 0
        step_y = 1 if ey > py else -1 if ey < py else 0
        nx, ny = ex + step_x, ey + step_y
        if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
            return
        if (nx, ny) in self.rocks:
            return
        if (nx, ny) == self.player_pos:
            return
        occupied = {pos for other, pos in self.enemy_positions.items() if other is not enemy and other.is_alive()}
        if (nx, ny) in occupied:
            return
        self.enemy_positions[enemy] = (nx, ny)
        self.add_log(f"Push mastery: {enemy.name} is shoved back.")

    def _apply_cleave_mastery(self, primary_target: Character) -> None:
        if self.cleave_used_this_turn:
            return
        if primary_target not in self.enemy_positions:
            return

        target_pos = self.enemy_positions[primary_target]
        candidates = []
        for enemy, pos in self.enemy_positions.items():
            if enemy is primary_target or not enemy.is_alive():
                continue
            if max(abs(pos[0] - target_pos[0]), abs(pos[1] - target_pos[1])) > 1:
                continue
            if max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1])) > self.player.get_attack_range():
                continue
            candidates.append(enemy)
        if not candidates:
            return

        self.cleave_used_this_turn = True
        secondary = candidates[0]
        dmg_num, dmg_die = self.player.get_damage_dice()
        damage = dice.roll_dice(dmg_num, dmg_die)
        ability_mod = self.player._get_weapon_attack_ability_modifier()
        if ability_mod < 0:
            damage += ability_mod
        damage = max(0, damage)
        if damage <= 0:
            return
        if hasattr(secondary, "take_damage"):
            dealt, _ = secondary.take_damage(damage, damage_type="physical", source=self.player, log_fn=self.add_log)
        else:
            secondary.hp -= damage
            dealt = damage
        self.add_log(f"Cleave mastery hits {secondary.name} for {dealt} damage.")

    def _apply_nick_mastery(self, primary_target: Character) -> None:
        if self.nick_used_this_turn:
            return
        offhand = self.player.equipped_offhand
        from items import Weapon
        if not isinstance(offhand, Weapon):
            return
        if not offhand.has_property("Light"):
            return

        self.nick_used_this_turn = True
        target = primary_target if primary_target.is_alive() else None
        if target is None:
            return

        roll = self.player.roll_d20()
        attack_bonus = self.player.get_attack_bonus_total() - self.player.get_attack_roll_penalty()
        total = roll + attack_bonus
        target_ac = target.get_ac() if hasattr(target, "get_ac") else target.ac
        if total < target_ac and roll != 20:
            self.add_log("Nick mastery offhand strike misses.")
            return

        damage = dice.roll_dice(offhand.dmg_num, offhand.dmg_die)
        ability_mod = self.player._get_weapon_attack_ability_modifier()
        if ability_mod < 0:
            damage += ability_mod
        damage = max(0, damage + offhand.dmg_bonus)
        if hasattr(target, "take_damage"):
            dealt, _ = target.take_damage(damage, damage_type="physical", source=self.player, log_fn=self.add_log)
        else:
            target.hp -= damage
            dealt = damage
        self.add_log(f"Nick mastery offhand strike hits {target.name} for {dealt} damage.")


def main():
    """Main game loop."""
    parser = argparse.ArgumentParser(description="D&D Roguelike GUI")
    parser.add_argument("--seed", type=int, help="Seed RNG for reproducible runs")
    parser.add_argument("--waves", type=int, default=3, help="Number of waves")
    parser.add_argument("--create-character", action="store_true", help="Run character creator (GUI by default, use --terminal-creator for text version)")
    parser.add_argument("--terminal-creator", action="store_true", help="Use terminal character creator instead of GUI")
    parser.add_argument("--quick-start", action="store_true", help="Skip character creator, use default Hero")
    args = parser.parse_args()
    
    if args.seed:
        random.seed(args.seed)
    
    # Create or load player
    if args.quick_start:
        # Use default hero
        stats = generate_level_1_stats("Fighter")
        player = Character(
            "Hero",
            hp=stats["hp"],
            ac=stats["ac"],
            attack_bonus=stats["attack_bonus"],
            dmg_num=stats["dmg_num"],
            dmg_die=stats["dmg_die"],
            dmg_bonus=stats["dmg_bonus"],
            initiative_bonus=stats["initiative_bonus"],
            class_name="Fighter",
            ability_scores=stats["ability_scores"],
            gold=50,
        )
    elif args.create_character and args.terminal_creator:
        # Terminal-based creator
        player = create_character_interactive()
    else:
        # Default: GUI character creator
        player = select_character_gui()
    
    # Initialize window
    window = GameWindow(cell_size=12, use_fullscreen=True)
    keep_state = KeepState()
    keep_state.ensure_season_raid_schedule(player.level)

    def apply_year_end_progression_hook(active_state: GameState | None = None) -> None:
        if not keep_state.consume_year_end_level_up_trigger():
            return
        year_message = f"Year-end reached: Year {keep_state.year} begins."
        if active_state is not None:
            active_state.add_log(year_message)
            active_state.add_log("Year-end progression hook available.")
            active_state.message = year_message
            active_state.message_timer = 90
        else:
            print(year_message)
            print("Year-end progression hook available.")

    def run_wave_intermission(active_state: GameState, wave_number: int) -> bool:
        rest_taken = False
        active_state.targeting_mode = False
        active_state.targeting_action = None
        active_state.spell_menu_open = False
        active_state.movement_max = max(1, player.get_speed_ft() // 5)
        active_state.movement_used = 0
        active_state.add_log(f"Wave {wave_number} cleared.")
        for line in active_state.wave_loot_lines():
            active_state.add_log(line)
        active_state.message = "Intermission: move, inspect sheet, and end day when ready."
        active_state.message_timer = 120

        def _level_up_modal() -> dict | None:
            if not active_state.pending_level_up_events:
                return None
            event = active_state.pending_level_up_events[0]
            from_level_raw = event.get("from_level", player.level - 1)
            to_level_raw = event.get("to_level", player.level)
            features_raw = event.get("features", [])

            from_level = int(from_level_raw) if isinstance(from_level_raw, (int, float)) else int(player.level - 1)
            to_level = int(to_level_raw) if isinstance(to_level_raw, (int, float)) else int(player.level)
            if isinstance(features_raw, list):
                features = [str(name) for name in features_raw]
            else:
                features = []

            lines = [
                f"{player.name} advanced from level {from_level} to level {to_level}.",
                f"Current XP: {player.xp}/{player.xp_to_next_level()} to next level.",
            ]
            if features:
                lines.append("Unlocked features:")
                for name in features:
                    lines.append(f"- {name}")
            else:
                lines.append("No new class features unlocked this level.")

            return {
                "title": "Level Up!",
                "lines": lines,
                "buttons": [("levelup_continue", "Continue")],
            }

        while window.running:
            intermission_actions = [
                (
                    "Long Rest" if not rest_taken else "Long Rest (done)",
                    "intermission_rest",
                    rest_taken,
                    "",
                ),
                ("End Day", "intermission_end_day", False, ""),
                ("Character Sheet", "character_sheet", False, ""),
            ]
            intermission_tooltips = {
                "intermission_rest": "Restore HP and class feature uses for next wave",
                "intermission_end_day": "Commit and advance the calendar day",
                "character_sheet": "Open character sheet (inventory, skills, proficiencies)",
            }

            status_msg = f"Intermission - {keep_state.status_line()} | Move, review menus, then End Day when ready."

            window.render(
                player,
                active_state.player_pos,
                active_state.enemies,
                active_state.enemy_positions,
                status_msg,
                combat_log=active_state.combat_log,
                spent_action=False,
                spent_bonus_action=False,
                hidden=active_state.hidden,
                targeting_mode=False,
                spell_menu_open=False,
                trees=active_state.trees,
                rocks=active_state.rocks,
                movement_used=active_state.movement_used,
                movement_max=active_state.movement_max,
                custom_actions=intermission_actions,
                custom_action_tooltips=intermission_tooltips,
                modal=_level_up_modal(),
                calendar_text=keep_state.status_line(),
                wave_number=wave_number,
                obstacles=active_state.obstacles,
            )

            clicked = window.handle_events()
            if not window.running:
                return False
            window.update_camera()

            if not clicked:
                continue

            if clicked.get("type") == "modal":
                if clicked.get("action") == "levelup_continue" and active_state.pending_level_up_events:
                    active_state.pending_level_up_events.pop(0)
                continue

            if clicked.get("type") == "action":
                action = clicked.get("action")
                if action == "intermission_rest" and not rest_taken:
                    if hasattr(player, "rest_features"):
                        player.rest_features()
                    player.hp = player.max_hp
                    player.temp_hp = 0
                    rest_taken = True
                    active_state.add_log("You take a long rest.")
                    active_state.message = "Rest complete: HP and features restored."
                    active_state.message_timer = 60
                    continue
                if action == "intermission_end_day":
                    keep_state.advance_raid_day(wave_number=wave_number, survived=True)
                    keep_state.ensure_season_raid_schedule(player.level)
                    apply_year_end_progression_hook(active_state)
                    active_state.add_log(f"Day ended. {keep_state.status_line()}.")
                    active_state.message = f"Day ended. {keep_state.status_line()}."
                    active_state.message_timer = 60
                    return True
                continue

            if clicked.get("type") == "grid":
                grid_x, grid_y = clicked["pos"]
                if (grid_x, grid_y) in active_state.obstacles:
                    active_state.message = "That tile is blocked."
                    active_state.message_timer = 30
                    continue
                active_state.movement_used = 0
                active_state.move_player(grid_x, grid_y)
        return False

    def run_game_over_screen(game_state: GameState, wave_number: int):
        """Show a game-over screen with stats and the last few combat-log lines.

        Blocks until the player clicks Quit or closes the window.
        """
        p = game_state.player
        stat_lines = [
            f"Name:    {p.name}",
            f"Species: {getattr(p, 'species', 'Unknown')}",
            f"Class:   {p.class_name}   Level: {p.level}",
            f"HP:      0 / {p.max_hp}   AC: {p.ac}",
            "",
            f"Gold:    {p.gold}",
            f"XP:      {p.xp}",
            f"Wave:    Fell on wave {wave_number}  (survived {wave_number - 1})",
            f"Date:    {keep_state.status_line()}",
        ]

        equipped_weapon = getattr(p, "equipped_weapon", None)
        equipped_armor = getattr(p, "equipped_armor", None)
        if equipped_weapon:
            stat_lines.append(f"Weapon:  {equipped_weapon}")
        if equipped_armor:
            stat_lines.append(f"Armor:   {equipped_armor}")

        # Show the last several log entries so the player can see what killed them
        log_snapshot = list(game_state.combat_log)[-8:]

        buttons = [("quit", "Quit")]

        while window.running:
            window.draw_game_over(
                title="You Have Fallen",
                stat_lines=stat_lines,
                log_lines=log_snapshot,
                buttons=buttons,
            )
            clicked = window.handle_events()
            if not window.running:
                break
            if clicked:
                action = clicked.get("action")
                if action == "quit":
                    break

    try:
        # Wave loop
        for wave in range(1, args.waves + 1):
            if not window.running:
                break
            
            # Spawn wave
            enemies = spawn_wave(wave)
            state = GameState(player, keep_state=keep_state)
            state.add_enemies(enemies)

            # Horn blast announcement
            horn_msg = state._generate_horn_blast_message()
            state.add_log(horn_msg)
            state.message = f"Wave {wave}! {horn_msg} Defend the keep!"
            state.message_timer = 90

            if hasattr(player, "restore_spell_slots"):
                player.restore_spell_slots()

            start_messages = player.start_combat(auto_features=False)
            if start_messages:
                state.message = f"{state.message} {start_messages[-1]}"
            
            # Battle loop
            while window.running and player.is_alive() and any(e.is_alive() for e in enemies):
                # Handle input
                clicked = window.handle_events()
                window.update_camera()

                # --- Handle trigger modal responses ---
                if clicked and state.turn_phase == "awaiting_trigger":
                    if clicked.get("type") == "modal":
                        accepted = clicked.get("action") == "trigger_accept"
                        state.resolve_current_trigger(accepted)
                        if not state.pending_triggers:
                            # All triggers resolved – resume the phase we came from
                            state.turn_phase = state._trigger_resume_phase
                    # While awaiting trigger, ignore other clicks
                    clicked = None

                if clicked and state.turn_phase == "player_input":
                    if clicked.get("type") == "action":
                        action = clicked.get("action")
                        if isinstance(action, str) and action.startswith("on_hit::"):
                            state.activate_pending_on_hit_action(action)
                            continue
                        if action and action.startswith("sheet::"):
                            parts = action.split("::")
                            sheet_action = parts[1] if len(parts) > 1 else ""
                            handled_sheet = False

                            if sheet_action == "unequip_weapon":
                                handled_sheet = player.unequip_weapon()
                                state.message = "Weapon unequipped." if handled_sheet else "No weapon equipped."
                            elif sheet_action == "unequip_armor":
                                handled_sheet = player.unequip_armor()
                                state.message = "Armor unequipped." if handled_sheet else "No armor equipped."
                            elif sheet_action == "unequip_offhand":
                                if player.equipped_offhand is not None:
                                    player.inventory.append(player.equipped_offhand)
                                    player.equipped_offhand = None
                                    handled_sheet = True
                                    state.message = "Offhand unequipped."
                                else:
                                    state.message = "No offhand equipped."
                            elif len(parts) >= 3 and parts[2].isdigit():
                                inv_index = int(parts[2])
                                if 0 <= inv_index < len(player.inventory):
                                    item = player.inventory[inv_index]
                                    item_kind = getattr(item, "kind", "")

                                    if sheet_action == "equip_weapon" and item_kind == "weapon":
                                        handled_sheet = player.equip_weapon(item)
                                        state.message = f"Equipped {getattr(item, 'name', 'weapon')} as main weapon." if handled_sheet else "Could not equip weapon."
                                    elif sheet_action == "equip_armor" and item_kind == "armor":
                                        handled_sheet = player.equip_armor(item)
                                        state.message = f"Equipped {getattr(item, 'name', 'armor')}." if handled_sheet else "Could not equip armor."
                                    elif sheet_action == "equip_offhand" and item_kind == "weapon":
                                        prev_offhand = player.equipped_offhand
                                        player.equipped_offhand = item
                                        if prev_offhand and prev_offhand not in player.inventory:
                                            player.inventory.append(prev_offhand)
                                        if item in player.inventory:
                                            player.inventory.remove(item)
                                        handled_sheet = True
                                        state.message = f"Equipped {getattr(item, 'name', 'weapon')} in offhand."
                                    else:
                                        state.message = "That item cannot be equipped there."
                                else:
                                    state.message = "Selected inventory item no longer exists."

                            if handled_sheet:
                                state.add_log(state.message)
                            state.message_timer = 35
                            continue
                        # Process SRD action with economy tracking
                        if action == "attack":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "attack"
                                state.spell_menu_open = False
                                state.message = "Select a target to attack."
                                state.message_timer = 40
                        elif action == "toggle_spells":
                            state.spell_menu_open = not state.spell_menu_open
                            state.message = "Spells opened." if state.spell_menu_open else "Spells closed."
                            state.message_timer = 20
                        elif action == "breath_weapon":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            elif not player.can_use_breath_weapon():
                                state.message = "Breath Weapon not available."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "breath_weapon"
                                state.spell_menu_open = False
                                state.message = "Select a target for Breath Weapon."
                                state.message_timer = 40
                        elif action == "species_magic":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            elif not player.has_species_magic():
                                state.message = "Species magic not available."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "species_magic"
                                state.spell_menu_open = False
                                state.message = f"Select a target for {player.get_species_magic_label()}."
                                state.message_timer = 40
                        elif isinstance(action, str) and action.startswith("spell::"):
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                spell_name = action.split("::", 1)[1]
                                target_mode = player.get_spell_target_mode(spell_name)
                                if target_mode in {"self", "self_or_ally"}:
                                    state._reveal_player_from_hidden(source="spell")
                                    player.cast_spell(spell_name, target=player, log_fn=state.add_log)
                                    state.message = f"Cast {spell_name}."
                                    state.message_timer = 40
                                    state.spend_action()
                                else:
                                    state.targeting_mode = True
                                    state.targeting_action = action
                                    state.spell_menu_open = False
                                    state.message = f"Select a target for {spell_name}."
                                    state.message_timer = 40
                        elif action == "dodge":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                player.defend(ac_bonus=2)
                                state.message = "Dodge: +2 AC this round."
                                state.message_timer = 40
                                state.add_log(state.message)
                                state.spend_action()
                        elif action == "use_item":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                healed = player.use_potion()
                                if healed:
                                    state.message = f"Potion heals {healed} HP."
                                else:
                                    state.message = "No potions left."
                                state.message_timer = 40
                                state.add_log(state.message)
                                state.spent_bonus_action = True
                        elif action == "stonecunning":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.use_stonecunning():
                                    state.spent_bonus_action = True
                                    state.message = "Stonecunning active: Tremorsense 60 ft."
                                else:
                                    state.message = "Stonecunning not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "adrenaline_rush":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                gained = player.use_adrenaline_rush()
                                if gained > 0:
                                    state.spent_bonus_action = True
                                    state.movement_max *= 2
                                    state.message = f"Adrenaline Rush: +{gained} temporary HP and Dash."
                                else:
                                    state.message = "Adrenaline Rush not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "cloud_jaunt":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            elif not player.can_use_cloud_jaunt():
                                state.message = "Cloud Jaunt not available."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "cloud_jaunt"
                                state.spell_menu_open = False
                                state.message = "Select a destination for Cloud Jaunt."
                                state.message_timer = 40
                        elif action == "large_form":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.activate_large_form():
                                    state.spent_bonus_action = True
                                    state.message = "Large Form activated (+10 speed)."
                                else:
                                    state.message = "Large Form not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "dash":
                            spent_type = state.spend_action_or_cunning_bonus()
                            if spent_type is None:
                                state.message = "You have already used your action and bonus action."
                                state.message_timer = 40
                            else:
                                state.movement_max *= 2
                                if spent_type == "bonus":
                                    state.message = "Cunning Action Dash: movement doubled."
                                else:
                                    state.message = "Dash: movement doubled."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "disengage":
                            spent_type = state.spend_action_or_cunning_bonus()
                            if spent_type is None:
                                state.message = "You have already used your action and bonus action."
                                state.message_timer = 40
                            else:
                                if spent_type == "bonus":
                                    state.message = "Cunning Action Disengage: enemies have disadvantage to attack you."
                                else:
                                    state.message = "Disengage: enemies have disadvantage to attack you."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "hide":
                            spent_type = state.spend_action_or_cunning_bonus()
                            if spent_type is None:
                                state.message = "You have already used your action and bonus action."
                                state.message_timer = 40
                            else:
                                _, hide_message = state.attempt_hide()
                                if spent_type == "bonus":
                                    state.message = f"Cunning Action Hide: {hide_message}"
                                else:
                                    state.message = hide_message
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "end_turn":
                            state.pending_on_hit_actions = {}
                            state.turn_phase = "processing"
                            state.player_turn_started = False
                            state.round_number += 1
                        elif action == "cancel_attack":
                            state.targeting_mode = False
                            state.targeting_action = None
                            state.message = "Attack mode canceled."
                            state.message_timer = 40
                        # Handle class features (optional bonus actions)
                        elif action == "rage":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.activate_rage():
                                    state.message = "You enter a Rage!"
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Rage not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "extend_rage":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.extend_rage():
                                    state.message = "You roar, extending your Rage!"
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "You are not raging."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "innate_sorcery":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.activate_innate_sorcery():
                                    state.message = "Innate Sorcery active! +1 spell DC, Advantage on spell attacks."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Innate Sorcery not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "second_wind":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                healed = player.use_second_wind()
                                if healed:
                                    state.message = f"Second Wind heals {healed} HP."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Second Wind not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "inspiration":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.use_bardic_inspiration():
                                    state.message = "Bardic Inspiration ready (+1d6)."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Inspiration not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "channel_divinity":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                healed = player.use_channel_divinity()
                                if healed:
                                    state.message = f"Channel Divinity heals {healed} HP."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Channel Divinity not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "lay_on_hands":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                heal_amount = min(5, player.lay_on_hands_pool)
                                healed = player.use_lay_on_hands(heal_amount)
                                if healed:
                                    state.message = f"Lay On Hands heals {healed} HP."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Lay On Hands not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "action_surge":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                feature = player.get_feature("Action Surge")
                                if feature and feature.use():
                                    state.spent_bonus_action = True
                                    state.gain_action(1)
                                    state.message = "Action Surge: gained one additional action this turn."
                                else:
                                    state.message = "Action Surge not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "wild_shape":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                if player.use_wild_shape():
                                    state.message = "Wild Shape: temporary HP and mobility increased."
                                    state.spend_action()
                                else:
                                    state.message = "Wild Shape not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "monk_focus":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.use_monk_focus():
                                    state.message = "Monk Focus empowered your next hit."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Monk Focus not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "smite":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                if player.arm_smite():
                                    state.message = "Smite armed for your next hit."
                                    state.spent_bonus_action = True
                                else:
                                    state.message = "Smite not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "hunters_mark":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "hunters_mark"
                                state.spell_menu_open = False
                                state.message = "Select a target for Hunter's Mark."
                                state.message_timer = 40
                        elif action == "martial_arts_strike":
                            if state.spent_bonus_action:
                                state.message = "You have already used your bonus action."
                                state.message_timer = 40
                            else:
                                state.targeting_mode = True
                                state.targeting_action = "martial_arts_strike"
                                state.spell_menu_open = False
                                state.message = "Select a target for Unarmed Strike."
                                state.message_timer = 40
                        elif action == "font_magic":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                if player.use_font_of_magic():
                                    state.message = "Font of Magic restored one spell slot."
                                    state.spend_action()
                                else:
                                    state.message = "Font of Magic not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                        elif action == "arcane_recovery":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                if player.use_arcane_recovery():
                                    state.message = "Arcane Recovery restored one spell slot."
                                    state.spend_action()
                                else:
                                    state.message = "Arcane Recovery not available."
                                state.message_timer = 40
                                state.add_log(state.message)
                    elif clicked.get("type") == "grid":
                        if state.targeting_mode:
                            acted = False
                            if state.targeting_action == "breath_weapon":
                                acted = state.breath_weapon_enemy_at(clicked["pos"])
                            elif state.targeting_action == "species_magic":
                                acted = state.species_magic_enemy_at(clicked["pos"])
                            elif state.targeting_action == "cloud_jaunt":
                                tx, ty = clicked["pos"]
                                px, py = state.player_pos
                                dist = max(abs(tx - px), abs(ty - py))
                                occupied = clicked["pos"] in state.enemy_positions.values()
                                blocked = clicked["pos"] in state.obstacles
                                if dist > 6:
                                    state.message = "Cloud Jaunt range is 30 ft (6 tiles)."
                                    state.message_timer = 30
                                elif occupied or blocked:
                                    state.message = "That destination is blocked."
                                    state.message_timer = 30
                                elif not player.use_cloud_jaunt():
                                    state.message = "Cloud Jaunt not available."
                                    state.message_timer = 30
                                else:
                                    state.player_pos = (tx, ty)
                                    state.compute_player_visibility()
                                    state.spent_bonus_action = True
                                    state.message = "Cloud Jaunt repositioned you."
                                    state.message_timer = 30
                                    state.add_log(state.message)
                                    acted = True
                            elif state.targeting_action and state.targeting_action.startswith("spell::"):
                                spell_name = state.targeting_action.split("::", 1)[1]
                                if player.get_spell_aoe(spell_name):
                                    acted = state.cast_aoe_spell_at(spell_name, clicked["pos"])
                                else:
                                    acted = state.cast_spell_at(spell_name, clicked["pos"])
                                # If the spell cannot be cast at all (no slots),
                                # exit targeting so the player isn't stuck.
                                if not acted and not player.can_cast_spell(spell_name):
                                    state.targeting_mode = False
                                    state.targeting_action = None
                            elif state.targeting_action == "hunters_mark":
                                acted = state.apply_hunters_mark_at(clicked["pos"])
                            elif state.targeting_action == "martial_arts_strike":
                                acted = state.apply_martial_arts_strike_at(clicked["pos"])
                            else:
                                acted = state.attack_enemy_at(clicked["pos"])
                            if acted:
                                state.targeting_mode = False
                                state.targeting_action = None
                        else:
                            grid_x, grid_y = clicked["pos"]
                            in_keep = window.is_in_keep(state.player_pos[0], state.player_pos[1])
                            current_is_gate = window.is_gate(state.player_pos[0], state.player_pos[1])
                            target_in_keep = window.is_in_keep(grid_x, grid_y)
                            target_is_gate = window.is_gate(grid_x, grid_y)
                            if (grid_x, grid_y) in state.obstacles:
                                state.message = "That tile is blocked."
                                state.message_timer = 30
                                continue

                            if in_keep and not target_in_keep and not target_is_gate and not current_is_gate:
                                gate_distance = max(
                                    abs(state.player_pos[0] - GATE_X),
                                    abs(state.player_pos[1] - GATE_Y),
                                )
                                target_distance = max(abs(grid_x - GATE_X), abs(grid_y - GATE_Y))
                                required = gate_distance + target_distance
                                remaining = max(0, state.movement_max - state.movement_used)
                                if required <= remaining:
                                    state.player_pos = (grid_x, grid_y)
                                    state.movement_used += required
                                    state.compute_player_visibility()
                                    state.message = "Passed through the gate."
                                    state.message_timer = 30
                                    continue
                                state.message = "You must exit through the gate."
                                state.message_timer = 30
                                continue
                            if not in_keep and target_in_keep and not target_is_gate:
                                gate_distance = max(
                                    abs(state.player_pos[0] - GATE_X),
                                    abs(state.player_pos[1] - GATE_Y),
                                )
                                target_distance = max(abs(grid_x - GATE_X), abs(grid_y - GATE_Y))
                                required = gate_distance + target_distance
                                remaining = max(0, state.movement_max - state.movement_used)
                                if required <= remaining:
                                    state.player_pos = (grid_x, grid_y)
                                    state.movement_used += required
                                    state.compute_player_visibility()
                                    state.message = "Passed through the gate."
                                    state.message_timer = 30
                                    continue
                                state.message = "You must enter through the gate."
                                state.message_timer = 30
                                continue
                            if target_is_gate or current_is_gate:
                                state.message = "Passing through the gate."
                                state.message_timer = 30
                            if window.is_keep_blocked(grid_x, grid_y):
                                state.message = "That corner is blocked by a tower."
                                state.message_timer = 30
                                continue
                            if state.move_player(grid_x, grid_y):
                                pass
                
                # Update game state
                state.update(window)

                aoe_preview_cells = None
                aoe_preview_valid = False
                if state.targeting_mode and state.targeting_action and state.targeting_action.startswith("spell::"):
                    spell_name = state.targeting_action.split("::", 1)[1]
                    if player.get_spell_aoe(spell_name):
                        mouse_grid = window.screen_to_grid(*pygame.mouse.get_pos())
                        if mouse_grid is not None:
                            aoe_preview_cells = state.get_spell_aoe_cells(spell_name, mouse_grid)
                            aoe_preview_valid = state._spell_target_in_range(spell_name, mouse_grid)
                
                # Render
                extra_actions, extra_tooltips = state.get_pending_on_hit_ui_actions()
                # Show trigger modal when awaiting player confirmation
                trigger_modal = state.get_current_trigger_modal() if state.turn_phase == "awaiting_trigger" else None
                window.render(
                    player,
                    state.player_pos,
                    enemies,
                    state.enemy_positions,
                    state.message,
                    combat_log=state.combat_log,
                    spent_action=state.spent_action,
                    spent_bonus_action=state.spent_bonus_action,
                    hidden=state.hidden,
                    targeting_mode=state.targeting_mode,
                    spell_menu_open=state.spell_menu_open,
                    aoe_preview_cells=aoe_preview_cells,
                    aoe_preview_valid=aoe_preview_valid,
                    trees=state.trees,
                    rocks=state.rocks,
                    movement_used=state.movement_used,
                    movement_max=state.movement_max,
                    extra_actions=extra_actions,
                    extra_action_tooltips=extra_tooltips,
                    round_number=state.round_number,
                    turn_phase=state.turn_phase,
                    calendar_text=keep_state.status_line(),
                    wave_number=wave,
                    obstacles=state.obstacles,
                    fog_visible_cells=state._visible_cells,
                    lit_cells=state.get_lit_cells(),
                    raid_sides=state.raid_sides,
                    modal=trigger_modal,
                    hidden_enemies=state.hidden_enemies,
                )
            
            if not player.is_alive():
                keep_state.advance_raid_day(wave_number=wave, survived=False)
                keep_state.ensure_season_raid_schedule(player.level)
                apply_year_end_progression_hook()
                run_game_over_screen(state, wave)
                break
            if not run_wave_intermission(state, wave):
                break
        else:
            print(f"Victory! Survived all {args.waves} waves.")
    
    finally:
        window.close()


if __name__ == "__main__":
    main()
