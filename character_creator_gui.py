"""Pygame-based character creator GUI."""
import pygame
from typing import Optional, Tuple
from character import Character
from class_features import get_class_feature_summaries
from class_definitions import generate_level_1_stats

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
    "Artificer": {"ac": 14, "attack_bonus": 2, "dmg_num": 1, "dmg_die": 6, "dmg_bonus": 1, "hp": 25, "init": 1},
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
        
        self.screen_state = "class_select"  # "class_select", "name_input", "review"
        self.selected_class: Optional[str] = None
        self.character_name = "Hero"
        self.running = True
        self.character: Optional[Character] = None
        
        # UI elements
        self.class_buttons = {}
        self._create_class_buttons()
        self.name_input_text = ""
        self.confirm_button = Button(300, 500, 200, 50, "Start Battle")
        
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
    
    def handle_events(self) -> bool:
        """Handle pygame events. Return False to quit."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hovers
        if self.screen_state == "class_select":
            for btn in self.class_buttons.values():
                btn.update_hover(mouse_pos)
        elif self.screen_state == "name_input":
            pass  # No hover buttons
        elif self.screen_state == "review":
            self.confirm_button.update_hover(mouse_pos)
        
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
                    
                    elif self.screen_state == "review":
                        if self.confirm_button.is_clicked(mouse_pos):
                            self._create_character()
                            return False  # Exit creator
            
            if event.type == pygame.KEYDOWN:
                if self.screen_state == "name_input":
                    if event.key == pygame.K_RETURN:
                        if len(self.name_input_text) > 0:
                            self.screen_state = "review"
                        return True
                    elif event.key == pygame.K_BACKSPACE:
                        self.name_input_text = self.name_input_text[:-1]
                        return True
                    elif len(self.name_input_text) < 20:
                        if event.unicode.isprintable():
                            self.name_input_text += event.unicode
                            return True
        
        return True
    
    def _create_character(self):
        """Create the character from selections."""
        if not self.selected_class:
            return
        
        # Generate stats from class and default ability scores
        stats = generate_level_1_stats(self.selected_class)
        
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
        )
    
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
    
    def draw_review(self):
        """Draw the character review screen."""
        title = self.font_large.render(f"{self.name_input_text} the {self.selected_class}", True, COLOR_TEXT)
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        
        assert self.selected_class is not None
        
        # Generate stats from class and default ability scores
        stats = generate_level_1_stats(self.selected_class)
        ability_scores = stats["ability_scores"]
        
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
        ]
        
        for stat_line in calc_stats:
            stat_text = self.font_medium.render(stat_line, True, COLOR_TEXT)
            self.screen.blit(stat_text, (30, y))
            y += 35
        
        # Display class features
        y += 10
        features_title = self.font_medium.render("Class Features:", True, COLOR_TEXT_SELECTED)
        self.screen.blit(features_title, (30, y))
        y += 35
        
        feature_summary = get_class_feature_summaries(self.selected_class)
        for line in feature_summary.split("\n"):
            feature_text = self.font_small.render(line, True, COLOR_TEXT)
            self.screen.blit(feature_text, (40, y))
            y += 20
        
        self.confirm_button.draw(self.screen, self.font_medium)
    
    def render(self):
        """Render the current screen."""
        self.screen.fill(COLOR_BG)
        
        if self.screen_state == "class_select":
            self.draw_class_select()
        elif self.screen_state == "name_input":
            self.draw_name_input()
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


def create_character_gui() -> Character:
    """Run the GUI character creator. Returns a Character."""
    creator = CharacterCreatorGUI()
    character = creator.run()
    return character or Character("Hero", hp=30, ac=15, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=3, initiative_bonus=2, class_name="Fighter")
