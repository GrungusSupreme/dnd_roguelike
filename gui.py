"""Pygame-based GUI for the D&D roguelike combat system.

Provides a visual battle grid with character positioning and movement.
"""
import pygame
import math
from typing import Tuple, Optional
from character import Character

# Colors
COLOR_BG = (10, 10, 20)           # Dark blue background
COLOR_GRID = (40, 40, 60)          # Grid lines
COLOR_KEEP = (30, 60, 30)          # Keep area (green tint)
COLOR_GATE = (120, 90, 50)         # Keep gate
COLOR_TOWER = (80, 80, 90)         # Keep corner blocks
COLOR_PLAYER = (0, 200, 100)       # Green for player
COLOR_ENEMY = (200, 50, 50)        # Red for enemies
COLOR_SELECTED = (255, 255, 0)     # Yellow for selection
COLOR_TEXT = (200, 200, 200)       # Light gray text
COLOR_HP_BG = (50, 50, 50)         # Health bar background
COLOR_HP_FULL = (0, 200, 0)        # Health bar green
COLOR_HP_LOW = (200, 50, 0)        # Health bar red
COLOR_BUTTON = (60, 90, 130)       # UI button
COLOR_BUTTON_HOVER = (80, 120, 170)
COLOR_BUTTON_TEXT = (230, 230, 230)
COLOR_TREE = (40, 90, 40)         # Trees (cover, no blocking)
COLOR_ROCK = (80, 80, 70)         # Rocks (cover + blocking)
COLOR_COVER = (200, 200, 80)       # Cover indicator
COLOR_THREAT_LOW = (120, 220, 120)
COLOR_THREAT_MED = (230, 220, 110)
COLOR_THREAT_HIGH = (255, 150, 90)
COLOR_THREAT_BOSS = (255, 90, 90)

GRID_WIDTH = 64
GRID_HEIGHT = 64
KEEP_SIZE = 8
KEEP_START_X = (GRID_WIDTH - KEEP_SIZE) // 2
KEEP_START_Y = (GRID_HEIGHT - KEEP_SIZE) // 2
GATE_WIDTH = 2
GATE_X = KEEP_START_X + (KEEP_SIZE // 2) - (GATE_WIDTH // 2)
GATE_Y = KEEP_START_Y + KEEP_SIZE - 1

SKILL_TO_ABILITY = {
    "Acrobatics": "DEX",
    "Animal Handling": "WIS",
    "Arcana": "INT",
    "Athletics": "STR",
    "Deception": "CHA",
    "History": "INT",
    "Insight": "WIS",
    "Intimidation": "CHA",
    "Investigation": "INT",
    "Medicine": "WIS",
    "Nature": "INT",
    "Perception": "WIS",
    "Performance": "CHA",
    "Persuasion": "CHA",
    "Religion": "INT",
    "Sleight of Hand": "DEX",
    "Stealth": "DEX",
    "Survival": "WIS",
}

class GameWindow:
    """Pygame window for rendering the battle grid."""
    
    def __init__(self, cell_size: int = 12, use_fullscreen: bool = True):
        """Initialize the game window.
        
        Args:
            cell_size: Base size of each grid cell in pixels
            use_fullscreen: Whether to size the window to the display
        """
        pygame.init()
        self.base_cell_size = cell_size
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.5
        self.camera_x = 0
        self.camera_y = 0
        self.pan_speed = 18
        self.base_panel_height = 200
        self.panel_height = self.base_panel_height
        self.ui_scale = 1.0
        self.user_zoomed = False

        display_info = pygame.display.Info()
        if use_fullscreen:
            self.width = max(800, display_info.current_w)
            self.height = max(600, display_info.current_h)
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        else:
            self.width = GRID_WIDTH * cell_size
            self.height = GRID_HEIGHT * cell_size + self.panel_height
            self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("D&D Roguelike - Battle Grid")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.running = True
        self.action_buttons = []
        self.sheet_buttons = []
        self.action_tooltips = {}
        self.show_inventory = False
        self.show_character_sheet = False
        self._update_ui_scale()
        self._fit_zoom_to_window()
        self._clamp_camera()

    @property
    def cell_size(self) -> int:
        return max(4, int(self.base_cell_size * self.zoom))

    def _update_ui_scale(self) -> None:
        base_height = GRID_HEIGHT * self.base_cell_size + self.base_panel_height
        target_scale = max(1.0, self.height / max(1, base_height))
        if abs(target_scale - self.ui_scale) < 0.01:
            return
        self.ui_scale = target_scale
        self.panel_height = int(self.base_panel_height * self.ui_scale)
        self.font_large = pygame.font.Font(None, max(12, int(24 * self.ui_scale)))
        self.font_small = pygame.font.Font(None, max(10, int(18 * self.ui_scale)))

    def _grid_view_height(self) -> int:
        return max(0, self.height - self.panel_height)

    def _grid_view_rect(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.width, self._grid_view_height())

    def _clamp_camera(self) -> None:
        grid_width_px = GRID_WIDTH * self.cell_size
        grid_height_px = GRID_HEIGHT * self.cell_size
        view_width = self.width
        view_height = self._grid_view_height()
        if grid_width_px <= view_width:
            self.camera_x = -((view_width - grid_width_px) // 2)
        else:
            max_x = grid_width_px - view_width
            self.camera_x = max(0, min(self.camera_x, max_x))

        if grid_height_px <= view_height:
            self.camera_y = -((view_height - grid_height_px) // 2)
        else:
            max_y = grid_height_px - view_height
            self.camera_y = max(0, min(self.camera_y, max_y))

    def _apply_zoom(self, new_zoom: float, pivot: Optional[Tuple[int, int]] = None) -> None:
        old_cell = self.cell_size
        self.zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        new_cell = self.cell_size

        if new_cell == old_cell:
            return

        if pivot is None:
            pivot = (self.width // 2, self._grid_view_height() // 2)

        px, py = pivot
        world_x = (self.camera_x + px) / old_cell
        world_y = (self.camera_y + py) / old_cell
        self.camera_x = int(world_x * new_cell - px)
        self.camera_y = int(world_y * new_cell - py)
        self._clamp_camera()
        self.user_zoomed = True

    def _fit_zoom_to_window(self) -> None:
        view_height = self._grid_view_height()
        if view_height <= 0:
            return
        scale_x = self.width / max(1, GRID_WIDTH * self.base_cell_size)
        scale_y = view_height / max(1, GRID_HEIGHT * self.base_cell_size)
        fit_zoom = min(scale_x, scale_y)
        self.zoom = max(self.min_zoom, min(self.max_zoom, fit_zoom))

    def _draw_button(self, rect: pygame.Rect, label: str, hover: bool = False, disabled: bool = False):
        if disabled:
            color = (60, 60, 70)  # Greyed out disabled state
            text_color = (100, 100, 110)
        else:
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            text_color = COLOR_BUTTON_TEXT
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, COLOR_GRID, rect, width=1)
        text = self.font_small.render(label, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def get_action_at(self, screen_pos: Tuple[int, int]) -> Optional[str]:
        for rect, action in self.action_buttons:
            if rect.collidepoint(screen_pos):
                return action
        return None

    def get_action_tooltip(self, screen_pos: Tuple[int, int]) -> Optional[str]:
        for rect, action in self.action_buttons:
            if rect.collidepoint(screen_pos):
                return self.action_tooltips.get(action)
        return None

    def get_sheet_action_at(self, screen_pos: Tuple[int, int]) -> Optional[str]:
        for rect, action in self.sheet_buttons:
            if rect.collidepoint(screen_pos):
                return action
        return None

    def _format_mod(self, value: int) -> str:
        return f"+{value}" if value >= 0 else str(value)

    def _skill_bonus(self, player: Character, skill_name: str) -> int:
        ability = SKILL_TO_ABILITY.get(skill_name, "INT")
        base = player.get_ability_modifier(ability)
        if skill_name in getattr(player, "skill_proficiencies", []):
            base += player.get_proficiency_bonus()
        return base

    def _draw_section_box(self, rect: pygame.Rect, title: str) -> int:
        pygame.draw.rect(self.screen, (22, 26, 40), rect)
        pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)
        title_text = self.font_small.render(title, True, (240, 220, 120))
        self.screen.blit(title_text, (rect.x + 8, rect.y + 6))
        return rect.y + 30

    def _clip_text_to_width(self, text: str, max_width: int) -> str:
        if max_width <= 8:
            return ""
        if self.font_small.size(text)[0] <= max_width:
            return text
        clipped = text
        while clipped and self.font_small.size(clipped + "...")[0] > max_width:
            clipped = clipped[:-1]
        return (clipped + "...") if clipped else ""

    def _get_enemy_type_color(self, character: Character) -> Tuple[int, int, int]:
        name = (character.name or "").lower()
        if "mage" in name or "shaman" in name or "warlock" in name:
            return (175, 95, 210)
        if "archer" in name or "skeleton" in name or "hunter" in name:
            return (220, 150, 80)
        if "champion" in name or "boss" in name or "troll" in name:
            return (185, 70, 70)
        if "healer" in name or getattr(character, "behavior", "") == "healer":
            return (100, 180, 210)
        return COLOR_ENEMY

    def _get_threat_color(self, character: Character) -> Tuple[int, int, int]:
        dmg_score = max(1, getattr(character, "dmg_num", 1)) * max(2, getattr(character, "dmg_die", 4))
        attack_score = max(0, getattr(character, "attack_bonus", 0))
        hp_score = max(1, getattr(character, "max_hp", 1))
        threat_score = attack_score + (dmg_score / 4) + (hp_score / 8)
        if threat_score >= 16:
            return COLOR_THREAT_BOSS
        if threat_score >= 11:
            return COLOR_THREAT_HIGH
        if threat_score >= 7:
            return COLOR_THREAT_MED
        return COLOR_THREAT_LOW
        
    def draw_grid(self):
        """Draw the battle grid."""
        grid_height_px = GRID_HEIGHT * self.cell_size
        grid_width_px = GRID_WIDTH * self.cell_size
        for x in range(GRID_WIDTH + 1):
            sx = x * self.cell_size - self.camera_x
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (sx, -self.camera_y),
                (sx, grid_height_px - self.camera_y)
            )
        for y in range(GRID_HEIGHT + 1):
            sy = y * self.cell_size - self.camera_y
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (-self.camera_x, sy),
                (grid_width_px - self.camera_x, sy)
            )
    
    def draw_keep(self):
        """Draw the defended keep area (highlighted)."""
        top_left = self.grid_to_screen(KEEP_START_X, KEEP_START_Y)
        keep_rect = pygame.Rect(
            top_left[0],
            top_left[1],
            KEEP_SIZE * self.cell_size,
            KEEP_SIZE * self.cell_size
        )
        pygame.draw.rect(self.screen, COLOR_KEEP, keep_rect, width=3)
        # Label
        text = self.font_small.render("KEEP", True, COLOR_KEEP)
        self.screen.blit(text, (top_left[0] + 5, top_left[1] + 5))

        gate_top_left = self.grid_to_screen(GATE_X, GATE_Y)
        gate_rect = pygame.Rect(
            gate_top_left[0],
            gate_top_left[1],
            GATE_WIDTH * self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, COLOR_GATE, gate_rect)

        corners = [
            (KEEP_START_X, KEEP_START_Y),
            (KEEP_START_X + KEEP_SIZE - 1, KEEP_START_Y),
            (KEEP_START_X, KEEP_START_Y + KEEP_SIZE - 1),
            (KEEP_START_X + KEEP_SIZE - 1, KEEP_START_Y + KEEP_SIZE - 1),
        ]
        for cx, cy in corners:
            corner_top_left = self.grid_to_screen(cx, cy)
            corner_rect = pygame.Rect(
                corner_top_left[0],
                corner_top_left[1],
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, COLOR_TOWER, corner_rect)
    
    def draw_character(self, x: int, y: int, character: Character, is_player: bool = False, highlight: bool = False, in_cover: bool = False):
        """Draw a character on the grid.
        
        Args:
            x: Grid X position
            y: Grid Y position
            character: Character object
            is_player: Whether this is the player character
        """
        color = COLOR_PLAYER if is_player else self._get_enemy_type_color(character)
        top_left = self.grid_to_screen(x, y)
        cx = top_left[0] + self.cell_size // 2
        cy = top_left[1] + self.cell_size // 2
        radius = self.cell_size // 3
        
        # Draw character circle
        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        if not is_player:
            pygame.draw.circle(self.screen, self._get_threat_color(character), (cx, cy), radius + 2, width=2)
        if highlight:
            pygame.draw.circle(self.screen, COLOR_SELECTED, (cx, cy), radius + 2, width=2)
        
        # Draw health bar above character
        hp_bar_width = self.cell_size - 2
        hp_bar_height = 3
        hp_bar_x = top_left[0] + 1
        hp_bar_y = top_left[1] - 6
        
        # Background (red)
        pygame.draw.rect(self.screen, COLOR_HP_LOW, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        # Foreground (green, based on health)
        if character.hp > 0:
            health_pct = character.hp / character.max_hp
            filled_width = int(hp_bar_width * health_pct)
            pygame.draw.rect(self.screen, COLOR_HP_FULL, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height))
        
        # Name label
        name_text = self.font_small.render(character.name, True, COLOR_TEXT)
        self.screen.blit(name_text, (top_left[0] + 2, top_left[1] + self.cell_size + 2))

        hp_label = self.font_small.render(f"{character.hp}/{character.max_hp}", True, COLOR_TEXT)
        self.screen.blit(hp_label, (top_left[0] + 2, top_left[1] + self.cell_size + 16))

        if in_cover:
            cover_text = self.font_small.render("C", True, COLOR_COVER)
            self.screen.blit(cover_text, (top_left[0] + 2, top_left[1] + 2))
    
    def draw_ui_panel(
        self,
        player: Character,
        enemies: list[Character],
        message: str = "",
        keep_status: str = "",
        combat_log: Optional[list[str]] = None,
        spent_action: bool = False,
        spent_bonus_action: bool = False,
        hidden: bool = False,
        targeting_mode: bool = False,
        spell_menu_open: bool = False,
        movement_used: int = 0,
        movement_max: int = 6,
    ):
        """Draw the UI panel at the bottom (stats, messages, etc)."""
        panel_y = self._grid_view_height()
        panel_height = self.panel_height
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 30), (0, panel_y, self.width, panel_height))
        pygame.draw.line(self.screen, COLOR_GRID, (0, panel_y), (self.width, panel_y), width=2)
        
        # Player stats
        y_offset = panel_y + int(10 * self.ui_scale)
        player_text = f"Player: {player.name} | HP {player.hp}/{player.max_hp} | AC {player.ac} | Level {player.level} | Range {player.attack_range}"
        text = self.font_small.render(player_text, True, COLOR_TEXT)
        self.screen.blit(text, (10, y_offset))
        
        # Enemy count & action economy
        y_offset += int(25 * self.ui_scale)
        alive_enemies = [e for e in enemies if e.is_alive()]
        remaining = max(0, movement_max - movement_used)
        action_state = "✓ Action" if not spent_action else "✗ Action"
        bonus_state = "✓ Bonus" if not spent_bonus_action else "✗ Bonus"
        hidden_state = "HIDDEN" if hidden else ""
        economy_text = f"Enemies: {len(alive_enemies)} | {action_state} | {bonus_state} | Move: {remaining}/{movement_max} | {hidden_state}".strip()
        text = self.font_small.render(economy_text, True, COLOR_SELECTED if hidden else COLOR_TEXT)
        self.screen.blit(text, (10, y_offset))

        if keep_status:
            y_offset += int(22 * self.ui_scale)
            keep_text = self.font_small.render(keep_status, True, (170, 210, 255))
            self.screen.blit(keep_text, (10, y_offset))

        slot_summary = player.get_spell_slots_summary() if hasattr(player, "get_spell_slots_summary") else ""
        if slot_summary:
            y_offset += int(22 * self.ui_scale)
            slot_text = self.font_small.render(f"Spell Slots: {slot_summary}", True, COLOR_SELECTED)
            self.screen.blit(slot_text, (10, y_offset))

        status_summary = player.get_status_summary() if hasattr(player, "get_status_summary") else ""
        if status_summary:
            y_offset += int(22 * self.ui_scale)
            status_text = self.font_small.render(f"Status: {status_summary}", True, (255, 180, 120))
            self.screen.blit(status_text, (10, y_offset))
        
        # Message
        if message:
            y_offset += int(25 * self.ui_scale)
            msg_text = self.font_small.render(message, True, COLOR_SELECTED)
            self.screen.blit(msg_text, (10, y_offset))

        y_offset += int(22 * self.ui_scale)
        legend_text = "Threat Ring: Green=Low  Yellow=Med  Orange=High  Red=Boss"
        legend = self.font_small.render(legend_text, True, (170, 190, 210))
        self.screen.blit(legend, (10, y_offset))

        # Combat log panel (right side)
        log_x = int(self.width * 0.55)
        log_y = panel_y + int(10 * self.ui_scale)
        log_w = self.width - log_x - int(10 * self.ui_scale)
        log_h = panel_height - int(20 * self.ui_scale)
        pygame.draw.rect(self.screen, (15, 15, 25), (log_x, log_y, log_w, log_h))
        pygame.draw.rect(self.screen, COLOR_GRID, (log_x, log_y, log_w, log_h), width=1)
        log_title = self.font_small.render("Combat Log", True, COLOR_TEXT)
        self.screen.blit(log_title, (log_x + 8, log_y + 6))

        if combat_log:
            max_lines = max(1, int((log_h - int(30 * self.ui_scale)) // (16 * self.ui_scale)))
            recent = combat_log[-max_lines:]
            line_y = log_y + int(30 * self.ui_scale)
            for line in recent:
                entry = self.font_small.render(line, True, COLOR_TEXT)
                self.screen.blit(entry, (log_x + 8, line_y))
                line_y += int(16 * self.ui_scale)

        self.action_buttons = []
        self.action_tooltips = {}
        
        # SRD Actions (Action economy-based)
        actions = []
        
        # Main SRD actions (use action)
        actions.append((
            "Attack" if not spent_action else "Attack (used)",
            "attack",
            spent_action,
            "Action"
        ))
        actions.append((
            "Dodge" if not spent_action else "Dodge (used)",
            "dodge",
            spent_action,
            "Action"
        ))
        actions.append((
            "Dash" if not spent_action else "Dash (used)",
            "dash",
            spent_action,
            "Action"
        ))
        actions.append((
            "Disengage" if not spent_action else "Disengage (used)",
            "disengage",
            spent_action,
            "Action"
        ))
        actions.append((
            "Hide" if not spent_action else "Hide (used)",
            "hide",
            spent_action,
            "Action"
        ))

        if player.can_use_breath_weapon():
            actions.append((
                f"Breath ({player.breath_weapon_uses_remaining}/{player.breath_weapon_uses_max})" if not spent_action else "Breath (used)",
                "breath_weapon",
                spent_action,
                "Action"
            ))

        if player.has_species_magic():
            actions.append((
                player.get_species_magic_label() if not spent_action else f"{player.get_species_magic_label()} (used)",
                "species_magic",
                spent_action,
                "Action"
            ))

        has_spells = hasattr(player, "get_combat_spells") and bool(player.get_combat_spells())
        if has_spells:
            actions.append((
                "Spells: Open" if not spell_menu_open else "Spells: Back",
                "toggle_spells",
                False,
                ""
            ))
            if spell_menu_open:
                for spell_name in player.get_combat_spells():
                    can_cast = player.can_cast_spell(spell_name)
                    is_disabled = spent_action or (not can_cast)
                    label = spell_name
                    if is_disabled and spent_action:
                        label = f"{spell_name} (used)"
                    elif not can_cast:
                        label = f"{spell_name} (no slot)"
                    actions.append((label, f"spell::{spell_name}", is_disabled, "Action"))
        
        # Bonus action
        actions.append((
            f"Use Item ({player.potions})" if not spent_bonus_action else f"Use Item (used)",
            "use_item",
            spent_bonus_action,
            "Bonus"
        ))

        actions.append((
            "Character Sheet",
            "character_sheet",
            False,
            ""
        ))

        if hasattr(player, "get_species_bonus_actions"):
            for label, action_name, uses_left, uses_max in player.get_species_bonus_actions():
                btn_label = f"{label} ({uses_left}/{uses_max})"
                is_disabled = spent_bonus_action
                if is_disabled:
                    btn_label = f"{btn_label} (used)"
                actions.append((btn_label, action_name, is_disabled, "Bonus"))
        
        # End turn
        actions.append((
            "End Turn",
            "end_turn",
            False,
            ""
        ))
        
        # Exit targeting mode
        if targeting_mode:
            actions.insert(1, ("Cancel", "cancel_attack", False, ""))
        
        self.action_tooltips = {
            "attack": "Attack a target (costs Action)",
            "dodge": "Dodge: gain +2 AC (costs Action)",
            "dash": "Dash: double movement (costs Action)",
            "disengage": "Disengage: enemies have disadvantage to hit (costs Action)",
            "hide": "Hide from enemies (costs Action)",
            "breath_weapon": "Use Dragonborn Breath Weapon (costs Action)",
            "species_magic": "Use lineage/legacy species magic (costs Action)",
            "toggle_spells": "Open/close your spell list",
            "use_item": "Use a potion (costs Bonus Action)",
            "character_sheet": "Open character sheet (inventory, skills, proficiencies)",
            "stonecunning": "Gain Tremorsense 60 ft for 10 minutes (Bonus Action)",
            "adrenaline_rush": "Gain temporary HP and Dash as a Bonus Action",
            "cloud_jaunt": "Teleport up to 30 ft (Bonus Action)",
            "large_form": "Become Large for 10 minutes (+10 speed) (Bonus Action)",
            "cancel_attack": "Cancel attack mode",
            "end_turn": "End your turn",
        }

        if has_spells and spell_menu_open:
            for spell_name in player.get_combat_spells():
                self.action_tooltips[f"spell::{spell_name}"] = f"Cast {spell_name} (costs Action)"
        
        # Class features (bonus actions)
        feature_map = {
            "Rage": ("Rage", "rage", "Bonus"),
            "Second Wind": ("Second Wind", "second_wind", "Bonus"),
            "Bardic Inspiration": ("Inspire", "inspiration", "Bonus"),
            "Channel Divinity": ("Channel Divinity", "channel_divinity", "Bonus"),
            "Lay On Hands": ("Lay On Hands", "lay_on_hands", "Bonus"),
            "Action Surge": ("Action Surge", "action_surge", "Bonus"),
        }

        for feature in player.get_available_features():
            if feature.name in feature_map:
                base_label, action, cost_type = feature_map[feature.name]
                if feature.name == "Lay On Hands":
                    label = f"{base_label} ({player.lay_on_hands_pool})"
                elif feature.max_uses is None:
                    label = base_label
                else:
                    label = f"{base_label} ({int(feature.uses_remaining)}/{feature.max_uses})"
                
                is_disabled = spent_bonus_action if cost_type == "Bonus" else False
                if is_disabled:
                    label = f"{label} (used)"
                
                actions.append((label, action, is_disabled, cost_type))
                self.action_tooltips[action] = feature.description

        btn_width = int(140 * self.ui_scale)
        btn_height = int(26 * self.ui_scale)
        padding = int(8 * self.ui_scale)
        start_x = int(10 * self.ui_scale)
        min_start_y = panel_y + int(85 * self.ui_scale)
        start_y = max(min_start_y, y_offset + int(14 * self.ui_scale))
        action_area_width = int(self.width * 0.52) - start_x
        max_cols = max(1, action_area_width // (btn_width + padding))
        panel_bottom = panel_y + panel_height

        mouse_pos = pygame.mouse.get_pos()
        for idx, action_data in enumerate(actions):
            # Handle both old 2-tuple and new 4-tuple formats for compatibility
            if len(action_data) == 2:
                label, action = action_data
                is_disabled = False
            else:
                label, action, is_disabled, cost_type = action_data
            
            row = idx // max_cols
            col = idx % max_cols
            x = start_x + col * (btn_width + padding)
            y = start_y + row * (btn_height + padding)
            if y + btn_height > panel_bottom - int(6 * self.ui_scale):
                continue
            rect = pygame.Rect(x, y, btn_width, btn_height)
            self.action_buttons.append((rect, action))
            self._draw_button(rect, label, rect.collidepoint(mouse_pos), disabled=is_disabled)
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen pixel coordinates."""
        return (
            grid_x * self.cell_size - self.camera_x,
            grid_y * self.cell_size - self.camera_y,
        )
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """Convert screen pixel coordinates to grid coordinates."""
        grid_y = self._grid_view_height()
        if screen_y >= grid_y:
            return None  # Clicked in UI panel

        grid_x = (screen_x + self.camera_x) // self.cell_size
        grid_y = (screen_y + self.camera_y) // self.cell_size
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            return (grid_x, grid_y)
        return None
    
    def is_in_keep(self, grid_x: int, grid_y: int) -> bool:
        """Check if a grid position is within the keep."""
        return (
            KEEP_START_X <= grid_x < KEEP_START_X + KEEP_SIZE
            and KEEP_START_Y <= grid_y < KEEP_START_Y + KEEP_SIZE
        )

    def is_keep_blocked(self, grid_x: int, grid_y: int) -> bool:
        """Check if a keep tile is blocked for towers/buildings."""
        if not self.is_in_keep(grid_x, grid_y):
            return False
        corners = {
            (KEEP_START_X, KEEP_START_Y),
            (KEEP_START_X + KEEP_SIZE - 1, KEEP_START_Y),
            (KEEP_START_X, KEEP_START_Y + KEEP_SIZE - 1),
            (KEEP_START_X + KEEP_SIZE - 1, KEEP_START_Y + KEEP_SIZE - 1),
        }
        return (grid_x, grid_y) in corners

    def is_gate(self, grid_x: int, grid_y: int) -> bool:
        if grid_y != GATE_Y:
            return False
        return GATE_X <= grid_x < GATE_X + GATE_WIDTH
    
    def draw_inventory(self, player: Character):
        """Backward-compatible inventory overlay entrypoint."""
        self.draw_character_sheet(player)

    def draw_character_sheet(self, player: Character):
        self.sheet_buttons = []
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        panel_width = min(1080, self.width - 40)
        panel_height = min(760, self.height - 40)
        panel_x = (self.width - panel_width) // 2
        panel_y = (self.height - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (28, 34, 54), panel_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, panel_rect, 2)

        title = f"{player.name} - Character Sheet"
        title_text = self.font_large.render(title, True, (255, 255, 120))
        self.screen.blit(title_text, (panel_x + 18, panel_y + 14))

        subtitle = (
            f"{player.class_name}  Lv{player.level}  |  HP {player.hp}/{player.max_hp}  |  AC {player.get_ac()}  "
            f"|  PB {self._format_mod(player.get_proficiency_bonus())}  |  Gold {player.gold}"
        )
        subtitle_text = self.font_small.render(subtitle, True, COLOR_TEXT)
        self.screen.blit(subtitle_text, (panel_x + 18, panel_y + 44))

        left_col_x = panel_x + 16
        mid_col_x = panel_x + panel_width // 3
        right_col_x = panel_x + (2 * panel_width) // 3
        col_width = panel_width // 3 - 22
        top_y = panel_y + 78

        ability_rect = pygame.Rect(left_col_x, top_y, col_width, 184)
        y = self._draw_section_box(ability_rect, "Abilities")
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            score = player.ability_scores.get(ability, 10)
            mod = player.get_ability_modifier(ability)
            line = f"{ability}: {score:>2} ({self._format_mod(mod)})"
            line_text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(line_text, (ability_rect.x + 12, y))
            y += 22

        equip_rect = pygame.Rect(left_col_x, top_y + 196, col_width, panel_height - 292)
        y = self._draw_section_box(equip_rect, "Equipment & Attunement")

        btn_w = 72
        btn_h = 20
        equip_btn_x = equip_rect.right - btn_w - 10

        weapon_text = player.equipped_weapon.name if player.equipped_weapon else "Empty"
        armor_text = player.equipped_armor.name if player.equipped_armor else "Empty"
        offhand_text = player.equipped_offhand.name if player.equipped_offhand else "Empty"

        equipment_lines = [
            (f"Weapon: {weapon_text}", "sheet::unequip_weapon" if player.equipped_weapon else ""),
            (f"Armor: {armor_text}", "sheet::unequip_armor" if player.equipped_armor else ""),
            (f"Offhand: {offhand_text}", "sheet::unequip_offhand" if player.equipped_offhand else ""),
            (f"Attack Range: {player.get_attack_range()}", ""),
            (f"Damage: {player.get_damage_dice()[0]}d{player.get_damage_dice()[1]}{self._format_mod(player.get_damage_bonus())}", ""),
        ]
        for line, action in equipment_lines:
            text_max_width = equip_rect.width - 24
            if action:
                text_max_width = max(40, equip_btn_x - (equip_rect.x + 12) - 8)
            line = self._clip_text_to_width(line, text_max_width)
            text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (equip_rect.x + 12, y))
            if action:
                button_rect = pygame.Rect(equip_btn_x, y - 1, btn_w, btn_h)
                self._draw_button(button_rect, "Unequip", button_rect.collidepoint(mouse_pos))
                self.sheet_buttons.append((button_rect, action))
            y += 22

        y += 4
        attune_title = self.font_small.render("Magic Attunement", True, (170, 210, 255))
        self.screen.blit(attune_title, (equip_rect.x + 12, y))
        y += 24

        attuned_items = []
        if hasattr(player, "attuned_magic_items"):
            value = getattr(player, "attuned_magic_items")
            if isinstance(value, list):
                attuned_items = value[:]
        for idx in range(3):
            slot_name = "Empty Slot"
            if idx < len(attuned_items):
                item = attuned_items[idx]
                slot_name = getattr(item, "name", str(item))
            line = self.font_small.render(f"Slot {idx + 1}: {slot_name}", True, COLOR_TEXT)
            self.screen.blit(line, (equip_rect.x + 12, y))
            y += 22

        skills_rect = pygame.Rect(mid_col_x, top_y, col_width, panel_height - 96)
        y = self._draw_section_box(skills_rect, "Skills")
        for skill_name, ability in sorted(SKILL_TO_ABILITY.items()):
            bonus = self._skill_bonus(player, skill_name)
            mark = "*" if skill_name in player.skill_proficiencies else " "
            line = f"{mark} {skill_name[:16]:<16} ({ability}) {self._format_mod(bonus):>3}"
            text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (skills_rect.x + 8, y))
            y += 20
            if y > skills_rect.bottom - 44:
                break

        prof_rect = pygame.Rect(right_col_x, top_y, col_width, 248)
        y = self._draw_section_box(prof_rect, "Proficiencies")

        prof_lines = []
        if player.skill_proficiencies:
            prof_lines.append("Skills:")
            for name in sorted(player.skill_proficiencies):
                prof_lines.append(f"- {name}")
        else:
            prof_lines.append("Skills: None")

        if player.tool_proficiencies:
            prof_lines.append("Tools:")
            for name in sorted(player.tool_proficiencies):
                prof_lines.append(f"- {name}")
        else:
            prof_lines.append("Tools: None")

        for line in prof_lines:
            text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (prof_rect.x + 8, y))
            y += 20
            if y > prof_rect.bottom - 16:
                break

        inv_rect = pygame.Rect(right_col_x, top_y + 260, col_width, panel_height - 356)
        y = self._draw_section_box(inv_rect, "Inventory")
        if player.inventory:
            for inv_index, item in enumerate(player.inventory):
                item_name = getattr(item, "name", str(item))
                item_kind = getattr(item, "kind", "")
                label = f"- {item_name}" if not item_kind else f"- {item_name} ({item_kind})"
                label_max_width = inv_rect.width - 20
                if item_kind == "weapon":
                    label_max_width = max(40, (inv_rect.right - 154) - (inv_rect.x + 8) - 8)
                elif item_kind == "armor":
                    label_max_width = max(40, (inv_rect.right - 82) - (inv_rect.x + 8) - 8)
                label = self._clip_text_to_width(label, label_max_width)
                text = self.font_small.render(label, True, COLOR_TEXT)
                self.screen.blit(text, (inv_rect.x + 8, y))

                if item_kind == "weapon":
                    main_rect = pygame.Rect(inv_rect.right - 154, y - 1, 66, 20)
                    off_rect = pygame.Rect(inv_rect.right - 82, y - 1, 66, 20)
                    self._draw_button(main_rect, "Main", main_rect.collidepoint(mouse_pos))
                    self._draw_button(off_rect, "Off", off_rect.collidepoint(mouse_pos))
                    self.sheet_buttons.append((main_rect, f"sheet::equip_weapon::{inv_index}"))
                    self.sheet_buttons.append((off_rect, f"sheet::equip_offhand::{inv_index}"))
                elif item_kind == "armor":
                    armor_rect = pygame.Rect(inv_rect.right - 82, y - 1, 66, 20)
                    self._draw_button(armor_rect, "Equip", armor_rect.collidepoint(mouse_pos))
                    self.sheet_buttons.append((armor_rect, f"sheet::equip_armor::{inv_index}"))

                y += 20
                if y > inv_rect.bottom - 16:
                    break
        else:
            text = self.font_small.render("(Inventory Empty)", True, COLOR_TEXT)
            self.screen.blit(text, (inv_rect.x + 8, y))

        hint = self.font_small.render("Press C, I, or ESC to close", True, (180, 180, 180))
        hint_rect = hint.get_rect(midbottom=(self.width // 2, panel_y + panel_height - 10))
        self.screen.blit(hint, hint_rect)
    
    def render(
        self,
        player: Character,
        player_pos: Tuple[int, int],
        enemies: list,
        enemy_positions: dict,
        message: str = "",
        keep_status: str = "",
        combat_log: Optional[list[str]] = None,
        spent_action: bool = False,
        spent_bonus_action: bool = False,
        hidden: bool = False,
        targeting_mode: bool = False,
        spell_menu_open: bool = False,
        aoe_preview_cells: Optional[set[Tuple[int, int]]] = None,
        aoe_preview_valid: bool = False,
        trees: Optional[set] = None,
        rocks: Optional[set] = None,
        movement_used: int = 0,
        movement_max: int = 6,
    ):
        """Render a frame of the game.
        
        Args:
            player: Player Character
            player_pos: Player (x, y) grid position
            enemies: List of enemy Characters
            enemy_positions: Dict mapping enemy to (x, y) position
            message: Optional message to display
            combat_log: Optional list of combat log strings
            spent_action: Whether standard action has been used
            spent_bonus_action: Whether bonus action has been used
            hidden: Whether player is currently hidden
            trees: Set of (x, y) tree positions (cover, no blocking)
            rocks: Set of (x, y) rock positions (cover + blocking)
        """
        self._update_ui_scale()
        self.screen.fill(COLOR_BG)

        grid_rect = self._grid_view_rect()
        self.screen.set_clip(grid_rect)

        # Draw grid and keep
        self.draw_grid()
        self.draw_keep()

        if trees:
            for ox, oy in trees:
                top_left = self.grid_to_screen(ox, oy)
                rect = pygame.Rect(top_left[0], top_left[1], self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, COLOR_TREE, rect)
        
        # Draw rocks (gray, blocking + cover)
        if rocks:
            for ox, oy in rocks:
                top_left = self.grid_to_screen(ox, oy)
                rect = pygame.Rect(top_left[0], top_left[1], self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, COLOR_ROCK, rect)
        
        # Draw characters
        player_cover = False
        all_cover = (trees or set()) | (rocks or set())
        if all_cover:
            player_cover = any(
                max(abs(ox - player_pos[0]), abs(oy - player_pos[1])) == 1
                for ox, oy in all_cover
            )
        self.draw_character(player_pos[0], player_pos[1], player, is_player=True, in_cover=player_cover)
        for enemy in enemies:
            if enemy.is_alive() and enemy in enemy_positions:
                pos = enemy_positions[enemy]
                distance = max(abs(pos[0] - player_pos[0]), abs(pos[1] - player_pos[1]))
                in_range = distance <= player.attack_range
                in_cover = False
                if all_cover:
                    in_cover = any(
                        max(abs(ox - pos[0]), abs(oy - pos[1])) == 1
                        for ox, oy in all_cover
                    )
                self.draw_character(pos[0], pos[1], enemy, is_player=False, highlight=in_range, in_cover=in_cover)

        if aoe_preview_cells:
            preview_color = (255, 120, 60) if aoe_preview_valid else (180, 70, 70)
            for cell_x, cell_y in aoe_preview_cells:
                top_left = self.grid_to_screen(cell_x, cell_y)
                rect = pygame.Rect(top_left[0], top_left[1], self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, preview_color, rect, width=2)
                fill = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                fill.fill((preview_color[0], preview_color[1], preview_color[2], 60))
                self.screen.blit(fill, top_left)

        self.screen.set_clip(None)
        
        # Draw UI panel
        self.draw_ui_panel(
            player,
            enemies,
            message,
            keep_status=keep_status,
            combat_log=combat_log,
            spent_action=spent_action,
            spent_bonus_action=spent_bonus_action,
            hidden=hidden,
            targeting_mode=targeting_mode,
            spell_menu_open=spell_menu_open,
            movement_used=movement_used,
            movement_max=movement_max,
        )

        tooltip = self.get_action_tooltip(pygame.mouse.get_pos())
        if tooltip:
            tooltip_surf = self.font_small.render(tooltip, True, COLOR_TEXT)
            tooltip_rect = tooltip_surf.get_rect()
            tooltip_rect.bottomleft = (10, self.height - 5)
            self.screen.blit(tooltip_surf, tooltip_rect)
        
        if self.show_character_sheet or self.show_inventory:
            self.draw_character_sheet(player)
        
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
    
    def handle_events(self) -> Optional[dict]:
        """Handle pygame events.
        
        Returns:
            Dict with type "grid" or "action" on click, or None otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None
            if event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self._update_ui_scale()
                if not self.user_zoomed:
                    self._fit_zoom_to_window()
                self._clamp_camera()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_character_sheet or self.show_inventory:
                    if event.button == 1:
                        sheet_action = self.get_sheet_action_at(event.pos)
                        if sheet_action:
                            return {"type": "action", "action": sheet_action}
                    continue
                if event.button == 1:  # Left click
                    action = self.get_action_at(event.pos)
                    if action:
                        if action == "character_sheet":
                            self.show_character_sheet = not self.show_character_sheet
                            self.show_inventory = False
                            return None
                        return {"type": "action", "action": action}
                    grid_pos = self.screen_to_grid(event.pos[0], event.pos[1])
                    if grid_pos:
                        return {"type": "grid", "pos": grid_pos}
                if event.button == 4:
                    self._apply_zoom(self.zoom + 0.1, pivot=event.pos)
                if event.button == 5:
                    self._apply_zoom(self.zoom - 0.1, pivot=event.pos)
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    self._apply_zoom(self.zoom + 0.1, pivot=pygame.mouse.get_pos())
                elif event.y < 0:
                    self._apply_zoom(self.zoom - 0.1, pivot=pygame.mouse.get_pos())
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_character_sheet or self.show_inventory:
                        self.show_character_sheet = False
                        self.show_inventory = False
                    else:
                        self.running = False
                if event.key == pygame.K_i:
                    self.show_character_sheet = not self.show_character_sheet
                    self.show_inventory = False
                if event.key == pygame.K_c:
                    self.show_character_sheet = not self.show_character_sheet
                    self.show_inventory = False
        return None

    def update_camera(self) -> None:
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        if keys[pygame.K_a]:
            dx -= self.pan_speed
        if keys[pygame.K_d]:
            dx += self.pan_speed
        if keys[pygame.K_w]:
            dy -= self.pan_speed
        if keys[pygame.K_s]:
            dy += self.pan_speed
        if dx or dy:
            self.camera_x += dx
            self.camera_y += dy
            self._clamp_camera()
    
    def close(self):
        """Close the pygame window."""
        pygame.quit()
