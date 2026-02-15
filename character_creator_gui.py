"""Pygame-based character creator GUI."""
import pygame
from typing import Optional, Tuple
from character import Character
from class_features import get_class_feature_summaries
from class_definitions import generate_level_1_stats, get_default_ability_scores
from character_creation_data import (
    ABILITY_CODES,
    ALL_SKILLS,
    ORIGIN_FEAT_OPTIONS,
    SPECIES_SPEED_FEET,
    SPECIES_OPTIONS,
    SPECIES_TRAIT_CHOICES,
    TOOL_PROFICIENCY_OPTIONS,
    point_buy_delta,
)
from presets import build_character_from_preset, load_presets, save_preset, delete_preset
from spell_data import get_class_spell_options, get_spellcasting_requirements, is_spellcaster_class

# Colors (match main GUI)
COLOR_BG = (10, 10, 20)
COLOR_TEXT = (200, 200, 200)
COLOR_TEXT_SELECTED = (255, 255, 0)
COLOR_TEXT_HOVER = (150, 250, 150)
COLOR_BUTTON = (50, 100, 150)
COLOR_BUTTON_HOVER = (100, 150, 200)
COLOR_BUTTON_ACTIVE = (50, 150, 50)
COLOR_BORDER = (100, 150, 200)

# Class templates (from creator.py, simplified)
CLASS_TEMPLATES = {
    "Barbarian": {"ac": 13, "attack_bonus": 4, "dmg_num": 1, "dmg_die": 12, "dmg_bonus": 3, "hp": 35, "init": 0},
    "Bard": {"ac": 14, "attack_bonus": 3, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 2, "hp": 25, "init": 2},
    "Cleric": {"ac": 16, "attack_bonus": 3, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 2, "hp": 28, "init": 0},
    "Druid": {"ac": 14, "attack_bonus": 2, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 1, "hp": 26, "init": 1},
    "Fighter": {"ac": 17, "attack_bonus": 5, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 3, "hp": 32, "init": 1},
    "Monk": {"ac": 15, "attack_bonus": 4, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 2, "hp": 24, "init": 3},
    "Paladin": {"ac": 16, "attack_bonus": 4, "dmg_num": 1, "dmg_die": 10, "dmg_bonus": 3, "hp": 30, "init": 0},
    "Ranger": {"ac": 15, "attack_bonus": 4, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 2, "hp": 27, "init": 2},
    "Rogue": {"ac": 16, "attack_bonus": 5, "dmg_num": 1, "dmg_die": 6, "dmg_bonus": 2, "hp": 22, "init": 3},
    "Sorcerer": {"ac": 13, "attack_bonus": 2, "dmg_num": 1, "dmg_die": 6, "dmg_bonus": 1, "hp": 23, "init": 1},
    "Warlock": {"ac": 13, "attack_bonus": 3, "dmg_num": 1, "dmg_die": 8, "dmg_bonus": 2, "hp": 24, "init": 1},
    "Wizard": {"ac": 12, "attack_bonus": 2, "dmg_num": 1, "dmg_die": 6, "dmg_bonus": 0, "hp": 21, "init": 2},
}

class Button:
    """Simple clickable button."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int] = COLOR_BUTTON):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.active = False
        
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        if self.active:
            color = COLOR_BUTTON_ACTIVE
        else:
            color = COLOR_BUTTON_HOVER if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_BORDER, self.rect, width=2)
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(pos)


class CharacterCreatorGUI:
    """Pygame GUI for character creation."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """Initialize the character creator."""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("D&D Roguelike - Character Creator")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        self.screen_state = "class_select"  # "class_select", "name_input", "point_buy", "origin_asi", "origin_feat_select", "skill_select", "tool_select", "spell_select", "species_select", "species_trait_select", "species_bonus_select", "equipment_select", "review"
        self.selected_class: Optional[str] = None
        self.character_name = "Hero"
        self.running = True
        self.character: Optional[Character] = None
        self.ability_scores = None
        self.point_buy_points = 27
        self.origin_asi_choice: Optional[str] = None  # "2_1" or "1_1_1"
        self.origin_asi_selected = []
        self.origin_asi_primary: Optional[str] = None
        self.origin_asi_secondary: Optional[str] = None
        self.selected_skills = []
        self.skill_options = []
        self.skill_needed = 0
        self.selected_tool: Optional[str] = None
        self.selected_species: Optional[str] = None
        self.species_traits = {}
        self.species_trait_keys = []
        self.species_trait_index = 0
        self.selected_origin_feat: Optional[str] = None
        self.bonus_origin_feat: Optional[str] = None
        self.bonus_skill: Optional[str] = None
        self.saved_preset_name: Optional[str] = None
        self.selected_spells = []
        self.spell_choice_requirements = {"cantrips": 0, "spells": 0, "ability": "INT"}
        self.spell_buttons = {}
        self.spell_continue_button = Button(600, 520, 140, 40, "Continue")
        self.species_bonus_skill_title_y = 390
        # Equipment selection
        self.equipment_budget = 100  # Starting gold
        self.equipment_spent = 0
        self.selected_weapon = None
        self.selected_armor = None
        self.available_weapons = []
        self.available_armor = []
        
        # UI elements
        self.class_buttons = {}
        self._create_class_buttons()
        self.point_buy_buttons = {}
        self.point_buy_reset_button = Button(60, 520, 140, 40, "Reset")
        self.point_buy_default_button = Button(230, 520, 160, 40, "Use Default")
        self.point_buy_continue_button = Button(600, 520, 140, 40, "Continue")
        self.origin_asi_ability_buttons = {}
        self.origin_asi_mode_buttons = {
            "2_1": Button(200, 200, 240, 40, "+2 / +1 Split"),
            "1_1_1": Button(460, 200, 240, 40, "+1 / +1 / +1 All"),
        }
        self.origin_asi_reset_button = Button(60, 520, 140, 40, "Reset")
        self.origin_asi_continue_button = Button(600, 520, 140, 40, "Continue")
        self.species_buttons = {}
        self._create_species_buttons()
        self.species_continue_button = Button(600, 520, 140, 40, "Continue")
        self.species_trait_buttons = {}
        self.origin_feat_buttons = {}
        self.origin_feat_continue_button = Button(600, 520, 140, 40, "Continue")
        self.skill_buttons = {}
        self.skill_continue_button = Button(600, 520, 140, 40, "Continue")
        self.tool_buttons = {}
        self.tool_continue_button = Button(600, 520, 140, 40, "Continue")
        self.species_bonus_feat_buttons = {}
        self.species_bonus_skill_buttons = {}
        self.species_bonus_continue_button = Button(600, 520, 140, 40, "Continue")
        self.weapon_buttons = {}
        self.armor_buttons = {}
        self.equipment_continue_button = Button(600, 520, 140, 40, "Continue")
        
        self.name_input_text = ""
        self.confirm_button = Button(300, 540, 200, 50, "Start Battle")
        self.save_preset_button = Button(60, 540, 180, 50, "Save Preset")
        
    def _create_class_buttons(self):
        """Create buttons for each class."""
        classes = list(CLASS_TEMPLATES.keys())
        cols = 4
        rows = 3
        btn_width = 170
        btn_height = 40
        start_x = 20
        start_y = 80
        spacing_x = 190
        spacing_y = 60
        
        for i, class_name in enumerate(classes):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.class_buttons[class_name] = Button(x, y, btn_width, btn_height, class_name)

    def _init_origin_asi_buttons(self):
        self.origin_asi_ability_buttons = {}
        cols = 3
        btn_width = 120
        btn_height = 40
        start_x = 120
        start_y = 300
        spacing_x = 160
        spacing_y = 60

        for i, ability in enumerate(ABILITY_CODES):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.origin_asi_ability_buttons[ability] = Button(x, y, btn_width, btn_height, ability)

    def _create_species_buttons(self):
        cols = 3
        btn_width = 230
        btn_height = 36
        start_x = 40
        start_y = 100
        spacing_x = 250
        spacing_y = 50

        for i, species in enumerate(SPECIES_OPTIONS):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.species_buttons[species] = Button(x, y, btn_width, btn_height, species)

    def _init_species_traits(self):
        self.species_traits = {}
        self.species_trait_keys = list(SPECIES_TRAIT_CHOICES.get(self.selected_species, {}).keys())
        self.species_trait_index = 0
        self._create_species_trait_buttons()

    def _create_species_trait_buttons(self):
        self.species_trait_buttons = {}
        if not self.selected_species or self.species_trait_index >= len(self.species_trait_keys):
            return
        trait_key = self.species_trait_keys[self.species_trait_index]
        options = SPECIES_TRAIT_CHOICES.get(self.selected_species, {}).get(trait_key, [])

        cols = 2
        btn_width = 320
        btn_height = 36
        start_x = 80
        start_y = 140
        spacing_x = 340
        spacing_y = 50
        for i, option in enumerate(options):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.species_trait_buttons[option] = Button(x, y, btn_width, btn_height, option)

    def _init_origin_feat_buttons(self):
        self.origin_feat_buttons = {}
        available_feats = list(ORIGIN_FEAT_OPTIONS)

        cols = 2
        btn_width = 320
        btn_height = 36
        start_x = 80
        start_y = 160
        spacing_x = 340
        spacing_y = 50
        for i, feat in enumerate(available_feats):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.origin_feat_buttons[feat] = Button(x, y, btn_width, btn_height, feat)

    def _init_species_bonus_choices(self):
        self.bonus_origin_feat = None
        self.bonus_skill = None
        self.species_bonus_feat_buttons = {}
        self.species_bonus_skill_buttons = {}

        need_human_feat = self.selected_species == "Human"
        need_human_skill = self.selected_species == "Human"
        need_elf_skill = self.selected_species == "Elf"

        if need_human_feat:
            feat_options = [feat for feat in ORIGIN_FEAT_OPTIONS if feat != self.selected_origin_feat]
            cols = 2
            btn_width = 320
            btn_height = 34
            start_x = 80
            start_y = 140
            spacing_x = 340
            spacing_y = 44
            for i, feat in enumerate(feat_options):
                row = i // cols
                col = i % cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.species_bonus_feat_buttons[feat] = Button(x, y, btn_width, btn_height, feat)

        skill_pool = []
        if need_human_skill:
            skill_pool = [skill for skill in ALL_SKILLS if skill not in self.selected_skills]
        elif need_elf_skill:
            elf_skill_options = ["Insight", "Perception", "Survival"]
            skill_pool = [skill for skill in elf_skill_options if skill not in self.selected_skills]

        if skill_pool:
            cols = 3
            btn_width = 220
            btn_height = 30
            start_x = 40
            start_y = 300 if need_human_feat else 200
            spacing_x = 245
            spacing_y = 34
            self.species_bonus_skill_title_y = start_y - 36
            for i, skill in enumerate(skill_pool):
                row = i // cols
                col = i % cols
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.species_bonus_skill_buttons[skill] = Button(x, y, btn_width, btn_height, skill)

    def _species_bonus_valid(self) -> bool:
        if self.selected_species == "Human":
            return self.bonus_origin_feat is not None and self.bonus_skill is not None
        if self.selected_species == "Elf":
            return self.bonus_skill is not None
        return True

    def _init_equipment_select(self):
        """Initialize equipment selection screen with weapons and armor available for the class."""
        from items import WEAPONS, ARMOR
        
        self.equipment_spent = 0
        self.selected_weapon = None
        self.selected_armor = None
        self.weapon_buttons = {}
        self.armor_buttons = {}
        
        # All weapons available (in real game, filter by proficiency)
        self.available_weapons = [name for name in WEAPONS.keys()]
        self.available_armor = [name for name in ARMOR.keys()]
        
        # Create weapon buttons
        cols = 2
        btn_width = 320
        btn_height = 28
        start_x = 40
        start_y = 100
        spacing_x = 340
        spacing_y = 35
        for i, weapon_name in enumerate(self.available_weapons):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.weapon_buttons[weapon_name] = Button(x, y, btn_width, btn_height, weapon_name)
        
        # Create armor buttons
        start_y = 350
        for i, armor_name in enumerate(self.available_armor):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.armor_buttons[armor_name] = Button(x, y, btn_width, btn_height, armor_name)

    def _origin_asi_is_valid(self) -> bool:
        if self.origin_asi_choice == "2_1":
            return (
                self.origin_asi_primary is not None
                and self.origin_asi_secondary is not None
                and self.origin_asi_primary != self.origin_asi_secondary
            )
        if self.origin_asi_choice == "1_1_1":
            return len(self.origin_asi_selected) == 3
        return False

    def _apply_origin_asi(self):
        if not self.origin_asi_choice:
            return
        if self.origin_asi_choice == "2_1":
            if self.origin_asi_primary:
                self.ability_scores[self.origin_asi_primary] = min(
                    20, self.ability_scores[self.origin_asi_primary] + 2
                )
            if self.origin_asi_secondary:
                self.ability_scores[self.origin_asi_secondary] = min(
                    20, self.ability_scores[self.origin_asi_secondary] + 1
                )
        elif self.origin_asi_choice == "1_1_1":
            for ability in self.origin_asi_selected:
                self.ability_scores[ability] = min(20, self.ability_scores[ability] + 1)

    def _init_point_buy(self):
        self.point_buy_points = 27
        self.ability_scores = {"STR": 8, "DEX": 8, "CON": 8, "INT": 8, "WIS": 8, "CHA": 8}
        self.point_buy_buttons = {}
        row_y = 140
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            minus_btn = Button(360, row_y - 8, 30, 30, "-")
            plus_btn = Button(440, row_y - 8, 30, 30, "+")
            self.point_buy_buttons[(ability, "-")] = minus_btn
            self.point_buy_buttons[(ability, "+")] = plus_btn
            row_y += 50

    def _apply_default_ability_scores(self):
        if not self.selected_class:
            return
        self.ability_scores = get_default_ability_scores(self.selected_class).copy()
        total_cost = 0
        for score in self.ability_scores.values():
            total_cost += point_buy_delta(8, score)
        self.point_buy_points = 27 - total_cost

    def _init_skill_select(self):
        self.skill_options = ALL_SKILLS
        self.skill_needed = 2
        self.selected_skills = []
        self.skill_buttons = {}

        cols = 3
        btn_width = 230
        btn_height = 32
        start_x = 40
        start_y = 120
        spacing_x = 250
        spacing_y = 44
        for i, skill in enumerate(self.skill_options):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.skill_buttons[skill] = Button(x, y, btn_width, btn_height, skill)

    def _init_tool_select(self):
        self.selected_tool = None
        self.tool_buttons = {}
        cols = 3
        btn_width = 230
        btn_height = 24
        start_x = 40
        start_y = 120
        spacing_x = 250
        spacing_y = 30
        for i, tool in enumerate(TOOL_PROFICIENCY_OPTIONS):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            self.tool_buttons[tool] = Button(x, y, btn_width, btn_height, tool)

    def _init_spell_select(self):
        self.selected_spells = []
        self.spell_buttons = {}
        if not self.selected_class:
            self.spell_choice_requirements = {"cantrips": 0, "spells": 0, "ability": "INT"}
            return
        self.spell_choice_requirements = get_spellcasting_requirements(self.selected_class)
        options = get_class_spell_options(self.selected_class)

        btn_width = 320
        btn_height = 32
        start_x = 40
        cantrip_y = 150
        spell_y = 370
        spacing_x = 340
        spacing_y = 40

        for i, spell_name in enumerate(options.get("cantrips", [])):
            row = i // 2
            col = i % 2
            x = start_x + col * spacing_x
            y = cantrip_y + row * spacing_y
            self.spell_buttons[spell_name] = Button(x, y, btn_width, btn_height, spell_name)

        for i, spell_name in enumerate(options.get("spells", [])):
            row = i // 2
            col = i % 2
            x = start_x + col * spacing_x
            y = spell_y + row * spacing_y
            self.spell_buttons[spell_name] = Button(x, y, btn_width, btn_height, spell_name)

    def _toggle_spell(self, spell_name: str):
        if not self.selected_class:
            return
        options = get_class_spell_options(self.selected_class)
        is_cantrip = spell_name in options.get("cantrips", [])
        if spell_name in self.selected_spells:
            self.selected_spells.remove(spell_name)
            self.spell_buttons[spell_name].active = False
            return

        selected_cantrips = [s for s in self.selected_spells if s in options.get("cantrips", [])]
        selected_level_spells = [s for s in self.selected_spells if s in options.get("spells", [])]
        if is_cantrip:
            if len(selected_cantrips) >= self.spell_choice_requirements.get("cantrips", 0):
                return
        else:
            if len(selected_level_spells) >= self.spell_choice_requirements.get("spells", 0):
                return

        self.selected_spells.append(spell_name)
        self.spell_buttons[spell_name].active = True

    def _spell_selection_is_valid(self) -> bool:
        if not self.selected_class:
            return True
        options = get_class_spell_options(self.selected_class)
        cantrips = [s for s in self.selected_spells if s in options.get("cantrips", [])]
        spells = [s for s in self.selected_spells if s in options.get("spells", [])]
        return (
            len(cantrips) == self.spell_choice_requirements.get("cantrips", 0)
            and len(spells) == self.spell_choice_requirements.get("spells", 0)
        )
    
    def handle_events(self) -> bool:
        """Handle pygame events. Return False to quit."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hovers
        if self.screen_state == "class_select":
            for btn in self.class_buttons.values():
                btn.update_hover(mouse_pos)
        elif self.screen_state == "name_input":
            pass  # No hover buttons
        elif self.screen_state == "point_buy":
            for btn in self.point_buy_buttons.values():
                btn.update_hover(mouse_pos)
            self.point_buy_reset_button.update_hover(mouse_pos)
            self.point_buy_default_button.update_hover(mouse_pos)
            self.point_buy_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "origin_asi":
            for btn in self.origin_asi_mode_buttons.values():
                btn.update_hover(mouse_pos)
            for btn in self.origin_asi_ability_buttons.values():
                btn.update_hover(mouse_pos)
            self.origin_asi_reset_button.update_hover(mouse_pos)
            self.origin_asi_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "species_select":
            for btn in self.species_buttons.values():
                btn.update_hover(mouse_pos)
            self.species_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "species_trait_select":
            for btn in self.species_trait_buttons.values():
                btn.update_hover(mouse_pos)
        elif self.screen_state == "species_bonus_select":
            for btn in self.species_bonus_feat_buttons.values():
                btn.update_hover(mouse_pos)
            for btn in self.species_bonus_skill_buttons.values():
                btn.update_hover(mouse_pos)
            self.species_bonus_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "skill_select":
            for btn in self.skill_buttons.values():
                btn.update_hover(mouse_pos)
            self.skill_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "tool_select":
            for btn in self.tool_buttons.values():
                btn.update_hover(mouse_pos)
            self.tool_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "spell_select":
            for btn in self.spell_buttons.values():
                btn.update_hover(mouse_pos)
            self.spell_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "origin_feat_select":
            for btn in self.origin_feat_buttons.values():
                btn.update_hover(mouse_pos)
            self.origin_feat_continue_button.update_hover(mouse_pos)
        elif self.screen_state == "review":
            self.confirm_button.update_hover(mouse_pos)
            self.save_preset_button.update_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.screen_state == "class_select":
                        for class_name, btn in self.class_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.selected_class = class_name
                                self.screen_state = "name_input"
                                self.name_input_text = ""
                                return True

                    elif self.screen_state == "point_buy":
                        for (ability, action), btn in self.point_buy_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self._update_point_buy(ability, action)
                                return True
                        if self.point_buy_reset_button.is_clicked(mouse_pos):
                            self._init_point_buy()
                            return True
                        if self.point_buy_default_button.is_clicked(mouse_pos):
                            self._apply_default_ability_scores()
                            return True
                        if self.point_buy_continue_button.is_clicked(mouse_pos):
                            self.origin_asi_choice = None
                            self.origin_asi_selected = []
                            self.origin_asi_primary = None
                            self.origin_asi_secondary = None
                            self._init_origin_asi_buttons()
                            self.screen_state = "origin_asi"
                            return True

                    elif self.screen_state == "origin_asi":
                        for mode, btn in self.origin_asi_mode_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.origin_asi_choice = mode
                                self.origin_asi_primary = None
                                self.origin_asi_secondary = None
                                for other_btn in self.origin_asi_mode_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                return True
                        for ability, btn in self.origin_asi_ability_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                if not self.origin_asi_choice:
                                    return True
                                if ability not in self.origin_asi_selected:
                                    if len(self.origin_asi_selected) < 3:
                                        self.origin_asi_selected.append(ability)
                                    return True

                                if self.origin_asi_choice == "1_1_1":
                                    self.origin_asi_selected.remove(ability)
                                    if self.origin_asi_primary == ability:
                                        self.origin_asi_primary = None
                                    if self.origin_asi_secondary == ability:
                                        self.origin_asi_secondary = None
                                    return True

                                # 2_1 mode: assign +2/+1 by clicking selected abilities
                                if self.origin_asi_primary == ability:
                                    self.origin_asi_primary = None
                                    return True
                                if self.origin_asi_secondary == ability:
                                    self.origin_asi_secondary = None
                                    return True
                                if self.origin_asi_primary is None:
                                    self.origin_asi_primary = ability
                                    return True
                                if self.origin_asi_secondary is None and ability != self.origin_asi_primary:
                                    self.origin_asi_secondary = ability
                                    return True

                                # Allow clearing a non-assigned selection if both slots are used
                                if ability in self.origin_asi_selected:
                                    self.origin_asi_selected.remove(ability)
                                return True
                        if self.origin_asi_reset_button.is_clicked(mouse_pos):
                            self.origin_asi_selected = []
                            self.origin_asi_primary = None
                            self.origin_asi_secondary = None
                            return True
                        if self.origin_asi_continue_button.is_clicked(mouse_pos):
                            if self._origin_asi_is_valid():
                                self._apply_origin_asi()
                                self._init_origin_feat_buttons()
                                self.screen_state = "origin_feat_select"
                                return True

                    elif self.screen_state == "species_select":
                        for species_name, btn in self.species_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.selected_species = species_name
                                for other_btn in self.species_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                self._init_species_traits()
                                return True
                        if self.species_continue_button.is_clicked(mouse_pos):
                            if self.selected_species:
                                if self.species_trait_keys:
                                    self.screen_state = "species_trait_select"
                                else:
                                    self.screen_state = "review"
                                return True

                    elif self.screen_state == "species_trait_select":
                        for option_name, btn in self.species_trait_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                trait_key = self.species_trait_keys[self.species_trait_index]
                                self.species_traits[trait_key] = option_name
                                self.species_trait_index += 1
                                if self.species_trait_index >= len(self.species_trait_keys):
                                    if self.selected_species in {"Human", "Elf"}:
                                        self._init_species_bonus_choices()
                                        self.screen_state = "species_bonus_select"
                                    else:
                                        self.screen_state = "review"
                                else:
                                    self._create_species_trait_buttons()
                                return True

                    elif self.screen_state == "species_bonus_select":
                        for feat_name, btn in self.species_bonus_feat_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.bonus_origin_feat = feat_name
                                for other_btn in self.species_bonus_feat_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                return True

                        for skill_name, btn in self.species_bonus_skill_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.bonus_skill = skill_name
                                for other_btn in self.species_bonus_skill_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                return True

                        if self.species_bonus_continue_button.is_clicked(mouse_pos):
                            if self._species_bonus_valid():
                                self.screen_state = "review"
                                return True

                    elif self.screen_state == "origin_feat_select":
                        for feat_name, btn in self.origin_feat_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.selected_origin_feat = feat_name
                                for other_btn in self.origin_feat_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                return True
                        if self.origin_feat_continue_button.is_clicked(mouse_pos):
                            if self.selected_origin_feat:
                                self._init_skill_select()
                                self.screen_state = "skill_select"
                                return True

                    elif self.screen_state == "skill_select":
                        for skill_name, btn in self.skill_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self._toggle_skill(skill_name)
                                return True
                        if self.skill_continue_button.is_clicked(mouse_pos):
                            if len(self.selected_skills) == self.skill_needed:
                                self._init_tool_select()
                                self.screen_state = "tool_select"
                                return True

                    elif self.screen_state == "tool_select":
                        for tool_name, btn in self.tool_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self.selected_tool = tool_name
                                for other_btn in self.tool_buttons.values():
                                    other_btn.active = False
                                btn.active = True
                                return True
                        if self.tool_continue_button.is_clicked(mouse_pos):
                            if self.selected_tool:
                                if self.selected_class and is_spellcaster_class(self.selected_class):
                                    self._init_spell_select()
                                    self.screen_state = "spell_select"
                                else:
                                    self._init_equipment_select()
                                    self.screen_state = "equipment_select"
                                return True

                    elif self.screen_state == "spell_select":
                        for spell_name, btn in self.spell_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                self._toggle_spell(spell_name)
                                return True
                        if self.spell_continue_button.is_clicked(mouse_pos):
                            if self._spell_selection_is_valid():
                                self._init_equipment_select()
                                self.screen_state = "equipment_select"
                                return True
                    
                    elif self.screen_state == "equipment_select":
                        # Handle weapon button clicks
                        for weapon_name, btn in self.weapon_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                # Toggle deselection if clicking already selected weapon
                                if self.selected_weapon == weapon_name:
                                    self.selected_weapon = None
                                    btn.active = False
                                    self.equipment_spent = 0
                                    if self.selected_armor:
                                        from items import ARMOR
                                        self.equipment_spent = ARMOR[self.selected_armor].value
                                else:
                                    self.selected_weapon = weapon_name
                                    for other_btn in self.weapon_buttons.values():
                                        other_btn.active = False
                                    btn.active = True
                                    # Check budget and update spent amount
                                    from items import WEAPONS, ARMOR
                                    cost = WEAPONS[weapon_name].value
                                    armor_cost = ARMOR[self.selected_armor].value if self.selected_armor else 0
                                    self.equipment_spent = cost + armor_cost
                                return True
                        
                        # Handle armor button clicks
                        for armor_name, btn in self.armor_buttons.items():
                            if btn.is_clicked(mouse_pos):
                                # Toggle deselection if clicking already selected armor
                                if self.selected_armor == armor_name:
                                    self.selected_armor = None
                                    btn.active = False
                                    self.equipment_spent = 0
                                    if self.selected_weapon:
                                        from items import WEAPONS
                                        self.equipment_spent = WEAPONS[self.selected_weapon].value
                                else:
                                    self.selected_armor = armor_name
                                    for other_btn in self.armor_buttons.values():
                                        other_btn.active = False
                                    btn.active = True
                                    # Check budget and update spent amount
                                    from items import ARMOR, WEAPONS
                                    armor_cost = ARMOR[armor_name].value
                                    weapon_cost = WEAPONS[self.selected_weapon].value if self.selected_weapon else 0
                                    self.equipment_spent = armor_cost + weapon_cost
                                return True
                        
                        # Continue to next stage (equipment is optional)
                        if self.equipment_continue_button.is_clicked(mouse_pos):
                            if self.equipment_spent <= self.equipment_budget:
                                self.screen_state = "species_select"
                                return True
                    
                    elif self.screen_state == "review":
                        if self.confirm_button.is_clicked(mouse_pos):
                            self._create_character()
                            return False  # Exit creator
                        if self.save_preset_button.is_clicked(mouse_pos):
                            self._save_preset()
                            return True
            
            if event.type == pygame.KEYDOWN:
                if self.screen_state == "name_input":
                    if event.key == pygame.K_RETURN:
                        if len(self.name_input_text) > 0:
                            self._init_point_buy()
                            self.screen_state = "point_buy"
                        return True
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input_text = self.name_input_text[:-1]
                        return True
                    elif len(self.name_input_text) < 20:
                        if event.unicode.isprintable():
                            self.name_input_text += event.unicode
                            return True
        
        return True

    def _update_point_buy(self, ability: str, action: str):
        if not self.ability_scores:
            return
        current = self.ability_scores[ability]
        if action == "+" and current < 15:
            delta = point_buy_delta(current, current + 1)
            if delta <= self.point_buy_points:
                self.ability_scores[ability] = current + 1
                self.point_buy_points -= delta
        if action == "-" and current > 8:
            delta = point_buy_delta(current, current - 1)
            self.ability_scores[ability] = current - 1
            self.point_buy_points -= delta

    def _toggle_skill(self, skill_name: str):
        if skill_name in self.selected_skills:
            self.selected_skills.remove(skill_name)
            self.skill_buttons[skill_name].active = False
            return
        if len(self.selected_skills) >= self.skill_needed:
            return
        self.selected_skills.append(skill_name)
        self.skill_buttons[skill_name].active = True
    
    def _create_character(self):
        """Create the character from selections."""
        if not self.selected_class:
            return

        class_ranges = {
            "Bard": 2,
            "Druid": 2,
            "Ranger": 3,
            "Rogue": 2,
            "Sorcerer": 3,
            "Warlock": 3,
            "Wizard": 3,
        }
        
        ability_scores = self.ability_scores or get_default_ability_scores(self.selected_class)
        stats = generate_level_1_stats(self.selected_class, ability_scores)
        
        origin_feats = [self.selected_origin_feat] if self.selected_origin_feat else []
        if self.bonus_origin_feat:
            origin_feats.append(self.bonus_origin_feat)
        tool_proficiencies = [self.selected_tool] if self.selected_tool else []
        final_skills = list(self.selected_skills)
        if self.bonus_skill and self.bonus_skill not in final_skills:
            final_skills.append(self.bonus_skill)

        speed_ft = SPECIES_SPEED_FEET.get(self.selected_species, 30)

        self.character = Character(
            self.name_input_text or "Hero",
            hp=stats["hp"],
            ac=stats["ac"],
            attack_bonus=stats["attack_bonus"],
            dmg_num=stats["dmg_num"],
            dmg_die=stats["dmg_die"],
            dmg_bonus=stats["dmg_bonus"],
            initiative_bonus=stats["initiative_bonus"],
            class_name=self.selected_class,
            ability_scores=stats["ability_scores"],
            attack_range=class_ranges.get(self.selected_class, 1),
            skill_proficiencies=final_skills,
            species=self.selected_species,
            species_traits=self.species_traits,
            origin_feats=origin_feats,
            speed_ft=speed_ft,
            tool_proficiencies=tool_proficiencies,
            spells=self.selected_spells,
            gold=100,
        )
        
        # Equip selected items
        if self.selected_weapon:
            from items import WEAPONS
            self.character.equip_weapon(WEAPONS[self.selected_weapon])
        
        if self.selected_armor:
            from items import ARMOR
            self.character.equip_armor(ARMOR[self.selected_armor])

    def _save_preset(self):
        if not self.selected_class:
            return
        preset = {
            "name": self.name_input_text or "Hero",
            "class_name": self.selected_class,
            "ability_scores": self.ability_scores or get_default_ability_scores(self.selected_class),
            "origin_feats": ([self.selected_origin_feat] if self.selected_origin_feat else []) + ([self.bonus_origin_feat] if self.bonus_origin_feat else []),
            "skill_proficiencies": list(self.selected_skills) + ([self.bonus_skill] if self.bonus_skill else []),
            "tool_proficiencies": [self.selected_tool] if self.selected_tool else [],
            "species": self.selected_species,
            "species_traits": dict(self.species_traits),
            "spells": list(self.selected_spells),
            "gold": 100,
        }
        save_preset(preset)
        self.saved_preset_name = preset["name"]

    def _get_class_range(self) -> int:
        class_ranges = {
            "Bard": 2,
            "Druid": 2,
            "Ranger": 3,
            "Rogue": 2,
            "Sorcerer": 3,
            "Warlock": 3,
            "Wizard": 3,
        }
        return class_ranges.get(self.selected_class or "", 1)
    
    def draw_class_select(self):
        """Draw the class selection screen."""
        title = self.font_large.render("Choose Your Class", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        
        for btn in self.class_buttons.values():
            btn.draw(self.screen, self.font_medium)
    
    def draw_name_input(self):
        """Draw the name input screen."""
        title = self.font_large.render(f"Name Your {self.selected_class}", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
        
        input_text = self.font_medium.render(self.name_input_text or "_", True, COLOR_TEXT_SELECTED)
        self.screen.blit(input_text, (self.width // 2 - input_text.get_width() // 2, 250))
        
        hint = self.font_small.render("Press ENTER to continue", True, COLOR_TEXT)
        self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, 350))

    def draw_point_buy(self):
        title = self.font_large.render("Point Buy", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        points_text = self.font_medium.render(f"Points Remaining: {self.point_buy_points}", True, COLOR_TEXT_SELECTED)
        self.screen.blit(points_text, (60, 70))

        row_y = 140
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            score = self.ability_scores.get(ability, 8) if self.ability_scores else 8
            label = self.font_medium.render(f"{ability}: {score}", True, COLOR_TEXT)
            self.screen.blit(label, (60, row_y - 6))
            self.point_buy_buttons[(ability, "-")].draw(self.screen, self.font_medium)
            self.point_buy_buttons[(ability, "+")].draw(self.screen, self.font_medium)
            row_y += 50

        hint = self.font_small.render("Scores range 8-15. Standard pool: 27 points.", True, COLOR_TEXT)
        self.screen.blit(hint, (60, 480))

        self.point_buy_reset_button.draw(self.screen, self.font_medium)
        self.point_buy_default_button.draw(self.screen, self.font_medium)
        self.point_buy_continue_button.draw(self.screen, self.font_medium)

    def draw_origin_asi(self):
        title = self.font_large.render("Custom Background - Ability Bonuses", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        instructions = [
            "Pick three different abilities.",
            "Then choose +2/+1 for two of them, or +1/+1/+1 for all three.",
            "Tip: In +2/+1 mode, click a selected ability to mark +2, then +1.",
        ]
        for i, line in enumerate(instructions):
            text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(text, (40, 100 + i * 24))

        for btn in self.origin_asi_mode_buttons.values():
            btn.draw(self.screen, self.font_medium)

        for ability, btn in self.origin_asi_ability_buttons.items():
            btn.active = ability in self.origin_asi_selected
            label = ability
            if self.origin_asi_choice == "2_1":
                if ability == self.origin_asi_primary:
                    label = f"{ability} (+2)"
                elif ability == self.origin_asi_secondary:
                    label = f"{ability} (+1)"
                elif ability in self.origin_asi_selected:
                    label = f"{ability} (sel)"
            elif self.origin_asi_choice == "1_1_1" and ability in self.origin_asi_selected:
                label = f"{ability} (+1)"
            btn.text = label
            btn.draw(self.screen, self.font_medium)

        selected_text = ", ".join(self.origin_asi_selected) if self.origin_asi_selected else "None"
        selected_line = self.font_small.render(f"Selected: {selected_text}", True, COLOR_TEXT)
        self.screen.blit(selected_line, (40, 470))

        if self.origin_asi_choice and not self._origin_asi_is_valid():
            error = self.font_small.render("Select three abilities and assign bonuses", True, (255, 100, 100))
            self.screen.blit(error, (40, 495))

        self.origin_asi_reset_button.draw(self.screen, self.font_medium)
        self.origin_asi_continue_button.draw(self.screen, self.font_medium)

    def draw_species_select(self):
        title = self.font_large.render("Choose Species", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        for btn in self.species_buttons.values():
            btn.draw(self.screen, self.font_small)

        self.species_continue_button.draw(self.screen, self.font_medium)

    def draw_species_trait_select(self):
        if not self.species_trait_keys or self.species_trait_index >= len(self.species_trait_keys):
            return
        trait_key = self.species_trait_keys[self.species_trait_index]
        title = self.font_large.render(f"Select {trait_key}", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        for btn in self.species_trait_buttons.values():
            btn.draw(self.screen, self.font_small)

    def draw_species_bonus_select(self):
        title = self.font_large.render("Species Bonus Traits", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        y = 80
        if self.selected_species == "Human":
            feat_title = self.font_medium.render("Human Versatile: choose an extra Origin Feat", True, COLOR_TEXT_SELECTED)
            self.screen.blit(feat_title, (40, y))
            y += 40
            for btn in self.species_bonus_feat_buttons.values():
                btn.draw(self.screen, self.font_small)

            skill_title = self.font_medium.render("Human Skillful: choose one extra skill proficiency", True, COLOR_TEXT_SELECTED)
            self.screen.blit(skill_title, (40, self.species_bonus_skill_title_y))
            for btn in self.species_bonus_skill_buttons.values():
                btn.draw(self.screen, self.font_small)
        elif self.selected_species == "Elf":
            elf_title = self.font_medium.render("Elf Keen Senses: choose one skill", True, COLOR_TEXT_SELECTED)
            self.screen.blit(elf_title, (40, y))
            for btn in self.species_bonus_skill_buttons.values():
                btn.draw(self.screen, self.font_small)

        if not self._species_bonus_valid():
            msg = self.font_small.render("Make all required selections to continue.", True, (255, 100, 100))
            self.screen.blit(msg, (40, 485))

        self.species_bonus_continue_button.draw(self.screen, self.font_medium)

    def draw_origin_feat_select(self):
        title = self.font_large.render("Origin Feats", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        for btn in self.origin_feat_buttons.values():
            btn.draw(self.screen, self.font_small)

        selected_text = self.selected_origin_feat or "None"
        selected_line = self.font_small.render(f"Selected: {selected_text}", True, COLOR_TEXT)
        self.screen.blit(selected_line, (40, 470))

        self.origin_feat_continue_button.draw(self.screen, self.font_medium)

    def draw_skill_select(self):
        title = self.font_large.render(f"Choose {self.skill_needed} Skills", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        for btn in self.skill_buttons.values():
            btn.draw(self.screen, self.font_small)

        selected_text = ", ".join(self.selected_skills) if self.selected_skills else "None"
        selected_line = self.font_small.render(f"Selected: {selected_text}", True, COLOR_TEXT)
        self.screen.blit(selected_line, (40, 470))

        self.skill_continue_button.draw(self.screen, self.font_medium)

    def draw_tool_select(self):
        title = self.font_large.render("Choose Tool Proficiency", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        for btn in self.tool_buttons.values():
            btn.draw(self.screen, self.font_small)

        selected_text = self.selected_tool or "None"
        selected_line = self.font_small.render(f"Selected: {selected_text}", True, COLOR_TEXT)
        self.screen.blit(selected_line, (40, 470))

        self.tool_continue_button.draw(self.screen, self.font_medium)

    def draw_spell_select(self):
        title = self.font_large.render("Choose Spells", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))

        if not self.selected_class:
            return
        options = get_class_spell_options(self.selected_class)
        selected_cantrips = [s for s in self.selected_spells if s in options.get("cantrips", [])]
        selected_spells = [s for s in self.selected_spells if s in options.get("spells", [])]

        req_cantrips = self.spell_choice_requirements.get("cantrips", 0)
        req_spells = self.spell_choice_requirements.get("spells", 0)

        line1 = self.font_small.render(
            f"Cantrips: {len(selected_cantrips)}/{req_cantrips}", True, COLOR_TEXT_SELECTED
        )
        self.screen.blit(line1, (40, 70))
        line2 = self.font_small.render(
            f"Level 1 Spells: {len(selected_spells)}/{req_spells}", True, COLOR_TEXT_SELECTED
        )
        self.screen.blit(line2, (40, 95))

        cantrip_header = self.font_medium.render("Cantrips", True, COLOR_TEXT)
        self.screen.blit(cantrip_header, (40, 120))
        lvl_header = self.font_medium.render("Level 1 Spells", True, COLOR_TEXT)
        self.screen.blit(lvl_header, (40, 340))

        for spell_name, btn in self.spell_buttons.items():
            btn.active = spell_name in self.selected_spells
            btn.draw(self.screen, self.font_small)

        if not self._spell_selection_is_valid():
            error = self.font_small.render("Select the exact required number of cantrips and spells.", True, (255, 100, 100))
            self.screen.blit(error, (40, 500))

        self.spell_continue_button.draw(self.screen, self.font_medium)
    
    def draw_equipment_select(self):
        """Draw the equipment selection screen."""
        from items import WEAPONS, ARMOR
        
        # Title with budget display
        remaining = self.equipment_budget - self.equipment_spent
        title = self.font_large.render("Equip Your Character (Optional)", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 10))
        
        budget_text = self.font_small.render(f"Equipment Budget: {remaining}/{self.equipment_budget} gp remaining", 
                                            True, COLOR_TEXT if remaining >= 0 else (255, 100, 100))
        self.screen.blit(budget_text, (20, 45))
        
        # Weapons section
        weapon_label = self.font_medium.render("Weapons (Optional):", True, COLOR_TEXT_SELECTED)
        self.screen.blit(weapon_label, (20, 75))
        
        for btn in self.weapon_buttons.values():
            btn.draw(self.screen, self.font_small)
        
        # Armor section
        armor_label = self.font_medium.render("Armor (Optional):", True, COLOR_TEXT_SELECTED)
        self.screen.blit(armor_label, (20, 325))
        
        for btn in self.armor_buttons.values():
            btn.draw(self.screen, self.font_small)
        
        # Preview stats
        preview_y = 480
        preview_text = "Preview: "
        if self.selected_weapon:
            weapon = WEAPONS[self.selected_weapon]
            preview_text += f"{self.selected_weapon} ({weapon.dmg_num}d{weapon.dmg_die}+DEX) | "
        if self.selected_armor:
            armor = ARMOR[self.selected_armor]
            preview_text += f"AC: {armor.ac_base}"
            if armor.ac_bonus_dex:
                preview_text += "+DEX"
            if armor.max_dex is not None:
                preview_text += f" (max +{armor.max_dex})"
        
        preview_line = self.font_small.render(preview_text or "No equipment selected (unarmed/unarmored)", True, COLOR_TEXT)
        self.screen.blit(preview_line, (20, preview_y))
        
        self.equipment_continue_button.draw(self.screen, self.font_medium)
    
    def draw_review(self):
        """Draw the character review screen."""
        title = self.font_large.render(f"{self.name_input_text} the {self.selected_class}", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        
        assert self.selected_class is not None
        
        ability_scores = self.ability_scores or get_default_ability_scores(self.selected_class)
        stats = generate_level_1_stats(self.selected_class, ability_scores)
        
        y = 150
        
        # Show ability scores
        ability_y = y
        abilities_text = self.font_small.render("Ability Scores:", True, COLOR_TEXT_SELECTED)
        self.screen.blit(abilities_text, (30, ability_y))
        ability_y += 25
        
        for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
            score = ability_scores[ability]
            mod = (score - 10) // 2
            mod_str = f"+{mod}" if mod >= 0 else f"{mod}"
            ability_line = self.font_small.render(f"  {ability} {score} ({mod_str})", True, COLOR_TEXT)
            self.screen.blit(ability_line, (40, ability_y))
            ability_y += 20
        
        # Show calculated stats
        y = ability_y + 10
        calc_stats = [
            f"HP: {stats['hp']}",
            f"AC: {stats['ac']}",
            f"Attack: +{stats['attack_bonus']}",
            f"Damage: {stats['dmg_num']}d{stats['dmg_die']}+{stats['dmg_bonus']}",
            f"Initiative: +{stats['initiative_bonus']}",
            f"Range: {self._get_class_range()}",
        ]
        
        for stat_line in calc_stats:
            stat_text = self.font_medium.render(stat_line, True, COLOR_TEXT)
            self.screen.blit(stat_text, (30, y))
            y += 35

        y += 10
        species_text = self.font_medium.render(
            f"Species: {self.selected_species or 'None'}", True, COLOR_TEXT
        )
        self.screen.blit(species_text, (30, y))
        y += 30

        if self.species_traits:
            traits_line = ", ".join(
                f"{key}: {value}" for key, value in self.species_traits.items()
            )
            traits_text = self.font_small.render(f"Traits: {traits_line}", True, COLOR_TEXT)
            self.screen.blit(traits_text, (30, y))
            y += 25

        feats_line = self.selected_origin_feat or "None"
        if self.bonus_origin_feat:
            feats_line = f"{feats_line}, {self.bonus_origin_feat}"
        feats_text = self.font_small.render(f"Origin Feats: {feats_line}", True, COLOR_TEXT)
        self.screen.blit(feats_text, (30, y))
        y += 30

        final_skills = list(self.selected_skills)
        if self.bonus_skill and self.bonus_skill not in final_skills:
            final_skills.append(self.bonus_skill)
        skills_text = ", ".join(final_skills) if final_skills else "None"
        skills_line = self.font_small.render(f"Skills: {skills_text}", True, COLOR_TEXT)
        self.screen.blit(skills_line, (30, y))
        y += 30

        tool_text = self.selected_tool or "None"
        tool_line = self.font_small.render(f"Tool: {tool_text}", True, COLOR_TEXT)
        self.screen.blit(tool_line, (30, y))
        y += 30

        spells_text = ", ".join(self.selected_spells) if self.selected_spells else "None"
        spells_line = self.font_small.render(f"Spells: {spells_text}", True, COLOR_TEXT)
        self.screen.blit(spells_line, (30, y))
        y += 30

        gold_line = self.font_small.render("Gold: 50 GP", True, COLOR_TEXT)
        self.screen.blit(gold_line, (30, y))
        y += 30
        
        # Display class features
        y += 10
        features_title = self.font_medium.render("Class Features:", True, COLOR_TEXT_SELECTED)
        self.screen.blit(features_title, (30, y))
        y += 35

        max_review_y = 495
        feature_summary = get_class_feature_summaries(self.selected_class)
        for line in feature_summary.split("\n"):
            if y > max_review_y:
                overflow = self.font_small.render("...", True, COLOR_TEXT)
                self.screen.blit(overflow, (40, max_review_y))
                break
            feature_text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(feature_text, (40, y))
            y += 20
        
        if self.saved_preset_name:
            saved_text = self.font_small.render(
                f"Preset saved: {self.saved_preset_name}", True, COLOR_TEXT_SELECTED
            )
            self.screen.blit(saved_text, (60, 510))

        self.save_preset_button.draw(self.screen, self.font_medium)
        self.confirm_button.draw(self.screen, self.font_medium)
    
    def render(self):
        """Render the current screen."""
        self.screen.fill(COLOR_BG)
        
        if self.screen_state == "class_select":
            self.draw_class_select()
        elif self.screen_state == "name_input":
            self.draw_name_input()
        elif self.screen_state == "point_buy":
            self.draw_point_buy()
        elif self.screen_state == "origin_asi":
            self.draw_origin_asi()
        elif self.screen_state == "species_select":
            self.draw_species_select()
        elif self.screen_state == "species_trait_select":
            self.draw_species_trait_select()
        elif self.screen_state == "species_bonus_select":
            self.draw_species_bonus_select()
        elif self.screen_state == "skill_select":
            self.draw_skill_select()
        elif self.screen_state == "tool_select":
            self.draw_tool_select()
        elif self.screen_state == "spell_select":
            self.draw_spell_select()
        elif self.screen_state == "equipment_select":
            self.draw_equipment_select()
        elif self.screen_state == "origin_feat_select":
            self.draw_origin_feat_select()
        elif self.screen_state == "review":
            self.draw_review()
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def run(self) -> Optional[Character]:
        """Run the character creator. Return created Character or None."""
        while self.running:
            self.running = self.handle_events()
            self.render()
        
        pygame.quit()
        return self.character


class PresetMenuGUI:
    """Simple menu to choose new character or load preset."""

    def __init__(self, width: int = 640, height: int = 480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("D&D Roguelike - Character Menu")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.running = True
        self.state = "menu"  # "menu" or "load"
        self.selection = None
        self.new_button = Button(220, 160, 200, 50, "New Character")
        self.load_button = Button(220, 230, 200, 50, "Load Preset")
        self.back_button = Button(20, 420, 120, 40, "Back")
        self.preset_buttons = {}
        self._init_preset_buttons()

    def _init_preset_buttons(self):
        self.preset_buttons = {}
        self.delete_buttons = {}
        presets = load_presets()
        cols = 1
        btn_width = 400
        btn_height = 32
        start_x = 50
        start_y = 120
        spacing_y = 40
        for i, preset in enumerate(presets):
            row = i // cols
            y = start_y + row * spacing_y
            name = preset.get("name", f"Preset {i + 1}")
            load_btn = Button(start_x, y, btn_width, btn_height, name)
            delete_btn = Button(start_x + btn_width + 10, y, 60, btn_height, "Delete")
            self.preset_buttons[name] = (load_btn, preset)
            self.delete_buttons[name] = delete_btn

    def _handle_menu_click(self, pos):
        if self.new_button.is_clicked(pos):
            self.selection = ("new", None)
            return False
        if self.load_button.is_clicked(pos):
            self._init_preset_buttons()
            self.state = "load"
        return True

    def _handle_load_click(self, pos):
        # Check delete buttons first
        for name, delete_btn in self.delete_buttons.items():
            if delete_btn.is_clicked(pos):
                delete_preset(name)
                self._init_preset_buttons()
                return True
        
        # Check load buttons
        for name, (btn, preset) in self.preset_buttons.items():
            if btn.is_clicked(pos):
                self.selection = ("load", preset)
                return False
        
        if self.back_button.is_clicked(pos):
            self.state = "menu"
        return True

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == "menu":
                self.new_button.update_hover(mouse_pos)
                self.load_button.update_hover(mouse_pos)
            else:
                self.back_button.update_hover(mouse_pos)
                for btn, _ in self.preset_buttons.values():
                    btn.update_hover(mouse_pos)
                for delete_btn in self.delete_buttons.values():
                    delete_btn.update_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.selection = None
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "menu":
                        self.running = self._handle_menu_click(mouse_pos)
                    else:
                        self.running = self._handle_load_click(mouse_pos)

            self.screen.fill(COLOR_BG)
            if self.state == "menu":
                title = self.font_large.render("Character Menu", True, COLOR_TEXT)
                self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 60))
                self.new_button.draw(self.screen, self.font_medium)
                self.load_button.draw(self.screen, self.font_medium)
            else:
                title = self.font_large.render("Select a Preset", True, COLOR_TEXT)
                self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 40))
                if not self.preset_buttons:
                    empty = self.font_medium.render("No presets found.", True, COLOR_TEXT)
                    self.screen.blit(empty, (self.width // 2 - empty.get_width() // 2, 160))
                for name, (btn, _) in self.preset_buttons.items():
                    btn.draw(self.screen, self.font_medium)
                    delete_btn = self.delete_buttons[name]
                    delete_btn.draw(self.screen, self.font_medium)
                self.back_button.draw(self.screen, self.font_medium)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        return self.selection


def select_character_gui() -> Character:
    """Show the new/load menu and return a Character."""
    menu = PresetMenuGUI()
    selection = menu.run()
    if selection and selection[0] == "load":
        preset = selection[1]
        return build_character_from_preset(preset)
    if selection and selection[0] == "new":
        return create_character_gui()
    return create_character_gui()


def create_character_gui() -> Character:
    """Run the GUI character creator. Returns a Character."""
    creator = CharacterCreatorGUI()
    character = creator.run()
    if character:
        return character
    stats = generate_level_1_stats("Fighter")
    return Character(
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
        attack_range=1,
        skill_proficiencies=[],
        tool_proficiencies=[],
        species=None,
        species_traits={},
        origin_feats=[],
        speed_ft=30,
        gold=50,
    )
