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
    
    def __init__(self, player: Character, keep_state: KeepState | None = None):
        self.player = player
        self.keep_state = keep_state
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
        self.last_known_player_pos = self.player_pos  # Where enemies last saw the player
        self.sneak_attack_used_this_turn = False  # True if sneak attack already used
        self.targeting_mode = False
        self.targeting_action = None
        self.spell_menu_open = False
        self.movement_max = max(1, self.player.get_speed_ft() // 5)
        self.movement_used = 0
        self.player_turn_started = False
        self.trees = set()  # Provide cover but don't block movement
        self.rocks = set()  # Provide cover and block movement
        self.obstacles = set()  # Blocking tiles (rocks only)
        
    def add_enemies(self, enemies: list):
        """Add enemies and place them on the grid (outer regions)."""
        self.enemies = enemies
        self._generate_obstacles()
        for enemy in enemies:
            # Spawn enemies on the outer edges
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            # Keep trying until we get a position outside the keep and not in a rock
            while (KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE and
                   KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE) or (x, y) in self.rocks:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
            self.enemy_positions[enemy] = (x, y)

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

    def _has_line_of_sight(self, start: tuple[int, int], end: tuple[int, int]) -> bool:
        """Return True if there is a clear line of sight between two cells.
        Only rocks block LOS, trees provide cover but don't block sight."""
        x0, y0 = start
        x1, y1 = end
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0

        while (x, y) != (x1, y1):
            # Only rocks block line of sight
            if (x, y) not in (start, end) and (x, y) in self.rocks:
                return False
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return True

    def _cover_bonus(self, target_pos: tuple[int, int]) -> int:
        """Return cover bonus if a tree or rock is adjacent to target."""
        tx, ty = target_pos
        # Check both trees and rocks for cover
        for ox, oy in self.trees | self.rocks:
            if max(abs(ox - tx), abs(oy - ty)) == 1:
                return 2
        return 0

    def add_log(self, text: str) -> None:
        if not text:
            return
        self.combat_log.append(text)
        if len(self.combat_log) > 200:
            self.combat_log = self.combat_log[-200:]

    def keep_status_line(self) -> str:
        if self.keep_state is None:
            return ""
        return self.keep_state.status_line()

    def can_use_action(self) -> bool:
        return self.actions_remaining > 0

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
        self.message = f"Moved {distance} spaces."
        self.message_timer = 20
        return True

    def attack_enemy_at(self, target_pos: tuple[int, int]) -> bool:
        """Attack an enemy at the target position. Return True if an attack occurred."""
        for enemy, pos in self.enemy_positions.items():
            if not enemy.is_alive():
                continue
            if pos != target_pos:
                continue
            
            # If hidden, reveal position on attack
            was_hidden = self.hidden
            if self.hidden:
                self.hidden = False
                self.add_log("You attack from hiding, revealing your position!")
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
            cover_bonus = self._cover_bonus(pos) if self.player.attack_range > 1 else 0
            original_cover = enemy.temp_ac_bonus
            enemy.temp_ac_bonus += cover_bonus
            self.player.attack(enemy, log_fn=self.add_log)
            enemy.temp_ac_bonus = original_cover
            if not enemy.is_alive():
                self.player.gold += enemy.bounty
                self.message = f"Defeated {enemy.name}! Looted {enemy.bounty} gold."
                self.message_timer = 40
                self.add_log(self.message)
                xp_gain = enemy.bounty * 10
                self.player.add_xp(xp_gain)
                self.add_log(f"Gained {xp_gain} XP.")
            else:
                self.message = f"Hit {enemy.name} for some damage!"
                self.message_timer = 30
                self.add_log(self.message)
            self.spend_action()
            return True
        self.message = "No enemy on that tile."
        self.message_timer = 30
        return False

    def breath_weapon_enemy_at(self, target_pos: tuple[int, int]) -> bool:
        """Use Dragonborn Breath Weapon on an enemy at target position."""
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
                self.player.gold += enemy.bounty
                self.message = f"Breath Weapon defeated {enemy.name}! Looted {enemy.bounty} gold."
                self.message_timer = 40
                self.add_log(self.message)
                xp_gain = enemy.bounty * 10
                self.player.add_xp(xp_gain)
                self.add_log(f"Gained {xp_gain} XP.")
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
                self.player.gold += enemy.bounty
                self.message = f"{self.player.get_species_magic_label()} defeated {enemy.name}! Looted {enemy.bounty} gold."
                self.message_timer = 40
                self.add_log(self.message)
                xp_gain = enemy.bounty * 10
                self.player.add_xp(xp_gain)
                self.add_log(f"Gained {xp_gain} XP.")
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

            distance = max(abs(pos[0] - self.player_pos[0]), abs(pos[1] - self.player_pos[1]))
            if distance > spell_range:
                self.message = "Target out of spell range."
                self.message_timer = 40
                return False
            if spell_range > 1 and not self._has_line_of_sight(self.player_pos, pos):
                self.message = "Line of sight blocked."
                self.message_timer = 40
                return False

            self.player.cast_spell(spell_name, target=enemy, log_fn=self.add_log)
            if not enemy.is_alive():
                self.player.gold += enemy.bounty
                self.message = f"{spell_name} defeated {enemy.name}! Looted {enemy.bounty} gold."
                self.message_timer = 40
                self.add_log(self.message)
                xp_gain = enemy.bounty * 10
                self.player.add_xp(xp_gain)
                self.add_log(f"Gained {xp_gain} XP.")
            else:
                self.message = f"{spell_name} hits {enemy.name}."
                self.message_timer = 30
                self.add_log(self.message)

            self.spend_action()
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
        if not self.player.can_cast_spell(spell_name):
            self.message = f"Cannot cast {spell_name} right now."
            self.message_timer = 40
            return False
        if not self._spell_target_in_range(spell_name, target_pos):
            self.message = "Target out of spell range or line of sight blocked."
            self.message_timer = 40
            return False

        aoe_cells = self.get_spell_aoe_cells(spell_name, target_pos)
        targets = [enemy for enemy, pos in self.enemy_positions.items() if enemy.is_alive() and pos in aoe_cells]

        self.player.cast_aoe_spell(spell_name, targets, log_fn=self.add_log)
        defeated = []
        for enemy in targets:
            if not enemy.is_alive():
                defeated.append(enemy)

        total_bounty = 0
        total_xp = 0
        for enemy in defeated:
            total_bounty += enemy.bounty
            total_xp += enemy.bounty * 10

        if total_bounty > 0:
            self.player.gold += total_bounty
            self.player.add_xp(total_xp)
            self.message = f"{spell_name} defeated {len(defeated)} enemy(s)! Looted {total_bounty} gold."
            self.message_timer = 40
            self.add_log(self.message)
            self.add_log(f"Gained {total_xp} XP.")
        else:
            self.message = f"{spell_name} resolves."
            self.message_timer = 30

        self.spend_action()
        return True
    
    def move_enemies(self):
        """Move enemies toward the player (within keep area)."""
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            if enemy not in self.enemy_positions:
                continue
            
            ex, ey = self.enemy_positions[enemy]
            px, py = self.last_known_player_pos if self.hidden else self.player_pos

            in_keep = KEEP_START_X <= ex < KEEP_START_X + KEEP_SIZE and KEEP_START_Y <= ey < KEEP_START_Y + KEEP_SIZE
            if in_keep:
                target_x, target_y = px, py
            else:
                target_x, target_y = GATE_X, GATE_Y

            dx = target_x - ex
            dy = target_y - ey
            distance = max(abs(dx), abs(dy))
            
            # Don't move if within attack range
            if distance <= enemy.attack_range:
                continue
            
            # Move one step closer
            new_x = ex + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = ey + (1 if dy > 0 else -1 if dy < 0 else 0)
            
            # Clamp to grid
            new_x = max(0, min(GRID_WIDTH - 1, new_x))
            new_y = max(0, min(GRID_HEIGHT - 1, new_y))
            
            next_in_keep = KEEP_START_X <= new_x < KEEP_START_X + KEEP_SIZE and KEEP_START_Y <= new_y < KEEP_START_Y + KEEP_SIZE
            is_gate = (new_y == GATE_Y and GATE_X <= new_x < GATE_X + GATE_WIDTH)
            # Only rocks block movement, not trees
            blocked = (new_x, new_y) in self.rocks
            if next_in_keep and not in_keep and not is_gate:
                candidates = [
                    (ex + (1 if dx > 0 else -1 if dx < 0 else 0), ey),
                    (ex, ey + (1 if dy > 0 else -1 if dy < 0 else 0)),
                ]
                moved = False
                for cx, cy in candidates:
                    cx = max(0, min(GRID_WIDTH - 1, cx))
                    cy = max(0, min(GRID_HEIGHT - 1, cy))
                    candidate_in_keep = KEEP_START_X <= cx < KEEP_START_X + KEEP_SIZE and KEEP_START_Y <= cy < KEEP_START_Y + KEEP_SIZE
                    candidate_is_gate = (cy == GATE_Y and GATE_X <= cx < GATE_X + GATE_WIDTH)
                    if candidate_in_keep and not candidate_is_gate:
                        continue
                    # Only rocks block movement
                    if (cx, cy) in self.rocks:
                        continue
                    self.enemy_positions[enemy] = (cx, cy)
                    moved = True
                    break
                if not moved:
                    continue
            elif blocked:
                continue
            else:
                self.enemy_positions[enemy] = (new_x, new_y)
    
    def resolve_combat(self):
        """Enemy attacks if in range and can see player."""
        px, py = self.player_pos
        
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue

            if getattr(enemy, "behavior", "") == "regenerator" and enemy.hp < enemy.max_hp:
                healed = enemy.heal(2)
                if healed > 0:
                    self.add_log(f"{enemy.name} regenerates {healed} HP.")
            
            if enemy not in self.enemy_positions:
                continue
            
            ex, ey = self.enemy_positions[enemy]
            
            distance = max(abs(ex - px), abs(ey - py))
            
            # If player is hidden, enemies can't attack even if in range
            if self.hidden:
                # But if in melee range of hiding player, they might stumble upon us
                # For now, hiding prevents attacks
                continue
            
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
                        continue
            
            if enemy.is_alive() and distance <= enemy.attack_range:
                attack_result = enemy.attack(self.player, log_fn=self.add_log)
                if getattr(enemy, "behavior", "") == "mage" and "-> HIT" in attack_result and self.player.is_alive():
                    if random.random() < 0.35:
                        self.player.apply_status_effect("poisoned", rounds=2, potency=2)
                        self.add_log(f"{enemy.name} inflicts Poisoned on {self.player.name} (2 rounds).")
                if not self.player.is_alive():
                    self.message = "You have been slain!"
                    self.message_timer = 60
                    self.add_log(self.message)
    
    def update(self, window: GameWindow):
        """Update game state each frame."""
        if self.pause_frames > 0:
            self.pause_frames -= 1
            if self.message_timer > 0:
                self.message_timer -= 1
            return
        
        if self.turn_phase == "player_input":
            if not self.player_turn_started:
                self.player.start_turn()
                self.movement_max = max(1, self.player.get_speed_ft() // 5)
                self.movement_used = 0
                self.actions_remaining = 1
                self.spent_action = False
                self.spent_bonus_action = False
                self.sneak_attack_used_this_turn = False
                self.spell_menu_open = False
                self.player_turn_started = True
            self.message = ">>> Your turn! Click to move or take an action <<<"
            self.message_timer = 999
            # Waiting for player input (handled in main loop)
            return
        
        if self.turn_phase == "processing":
            # Move enemies
            self.move_enemies()
            self.pause_frames = 30  # Show movement for 0.5 seconds
            
            # Resolve combat
            self.resolve_combat()

            for message in self.player.end_round():
                self.message = message
                self.message_timer = 40
            
            # Switch back to player input
            self.turn_phase = "player_input"
            self.pause_frames = 30
            self.targeting_mode = False
            self.targeting_action = None
            self.movement_used = 0
            self.player_turn_started = False
        
        if self.message_timer > 0:
            self.message_timer -= 1


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
    
    try:
        # Wave loop
        for wave in range(1, args.waves + 1):
            if not window.running:
                break
            
            # Spawn wave
            enemies = spawn_wave(wave)
            state = GameState(player, keep_state=keep_state)
            state.add_enemies(enemies)
            state.message = f"Wave {wave}! Defend the keep! {keep_state.status_line()}"
            state.message_timer = 60

            if hasattr(player, "restore_spell_slots"):
                player.restore_spell_slots()

            start_messages = player.start_combat(auto_features=True)
            if start_messages:
                state.message = f"{state.message} {start_messages[-1]}"
            
            # Battle loop
            while window.running and player.is_alive() and any(e.is_alive() for e in enemies):
                # Handle input
                clicked = window.handle_events()
                window.update_camera()
                if clicked and state.turn_phase == "player_input":
                    if clicked.get("type") == "action":
                        action = clicked.get("action")
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
                        elif action.startswith("spell::"):
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                spell_name = action.split("::", 1)[1]
                                target_mode = player.get_spell_target_mode(spell_name)
                                if target_mode in {"self", "self_or_ally"}:
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
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                state.movement_max *= 2
                                state.message = "Dash: movement doubled."
                                state.message_timer = 40
                                state.add_log(state.message)
                                state.spend_action()
                        elif action == "disengage":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                state.message = "Disengage: enemies have disadvantage to attack you."
                                state.message_timer = 40
                                state.add_log(state.message)
                                state.spend_action()
                        elif action == "hide":
                            if not state.can_use_action():
                                state.message = "You have already used your action."
                                state.message_timer = 40
                            else:
                                state.hidden = True
                                state.message = "Hide: you slip out of sight. Enemies won't see you until you attack."
                                state.message_timer = 40
                                state.add_log(state.message)
                                state.spend_action()
                        elif action == "end_turn":
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
                window.render(
                    player,
                    state.player_pos,
                    enemies,
                    state.enemy_positions,
                    state.message,
                    keep_status=state.keep_status_line(),
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
                )
            
            if not player.is_alive():
                for update in keep_state.advance_raid_day(wave_number=wave, survived=False):
                    print(update)
                print(f"Game Over! Survived {wave - 1} waves.")
                break
            for update in keep_state.advance_raid_day(wave_number=wave, survived=True):
                print(update)
        else:
            print(f"Victory! Survived all {args.waves} waves.")
    
    finally:
        window.close()


if __name__ == "__main__":
    main()
