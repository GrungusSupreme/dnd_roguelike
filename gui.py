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
COLOR_PLAYER = (0, 200, 100)       # Green for player
COLOR_ENEMY = (200, 50, 50)        # Red for enemies
COLOR_SELECTED = (255, 255, 0)     # Yellow for selection
COLOR_TEXT = (200, 200, 200)       # Light gray text
COLOR_HP_BG = (50, 50, 50)         # Health bar background
COLOR_HP_FULL = (0, 200, 0)        # Health bar green
COLOR_HP_LOW = (200, 50, 0)        # Health bar red

GRID_WIDTH = 64
GRID_HEIGHT = 64
KEEP_SIZE = 8
KEEP_START_X = (GRID_WIDTH - KEEP_SIZE) // 2
KEEP_START_Y = (GRID_HEIGHT - KEEP_SIZE) // 2

class GameWindow:
    """Pygame window for rendering the battle grid."""
    
    def __init__(self, cell_size: int = 12):
        """Initialize the game window.
        
        Args:
            cell_size: Size of each grid cell in pixels
        """
        pygame.init()
        self.cell_size = cell_size
        self.width = GRID_WIDTH * cell_size
        self.height = GRID_HEIGHT * cell_size + 200  # Extra space for UI
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("D&D Roguelike - Battle Grid")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        self.running = True
        
    def draw_grid(self):
        """Draw the battle grid."""
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (x * self.cell_size, 0),
                (x * self.cell_size, GRID_HEIGHT * self.cell_size)
            )
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (0, y * self.cell_size),
                (GRID_WIDTH * self.cell_size, y * self.cell_size)
            )
    
    def draw_keep(self):
        """Draw the defended keep area (highlighted)."""
        keep_rect = pygame.Rect(
            KEEP_START_X * self.cell_size,
            KEEP_START_Y * self.cell_size,
            KEEP_SIZE * self.cell_size,
            KEEP_SIZE * self.cell_size
        )
        pygame.draw.rect(self.screen, COLOR_KEEP, keep_rect, width=3)
        # Label
        text = self.font_small.render("KEEP", True, COLOR_KEEP)
        self.screen.blit(text, (KEEP_START_X * self.cell_size + 5, KEEP_START_Y * self.cell_size + 5))
    
    def draw_character(self, x: int, y: int, character: Character, is_player: bool = False):
        """Draw a character on the grid.
        
        Args:
            x: Grid X position
            y: Grid Y position
            character: Character object
            is_player: Whether this is the player character
        """
        color = COLOR_PLAYER if is_player else COLOR_ENEMY
        cx = x * self.cell_size + self.cell_size // 2
        cy = y * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3
        
        # Draw character circle
        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        
        # Draw health bar above character
        hp_bar_width = self.cell_size - 2
        hp_bar_height = 3
        hp_bar_x = x * self.cell_size + 1
        hp_bar_y = y * self.cell_size - 6
        
        # Background (red)
        pygame.draw.rect(self.screen, COLOR_HP_LOW, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        # Foreground (green, based on health)
        if character.hp > 0:
            health_pct = character.hp / character.max_hp
            filled_width = int(hp_bar_width * health_pct)
            pygame.draw.rect(self.screen, COLOR_HP_FULL, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height))
        
        # Name label
        name_text = self.font_small.render(character.name, True, COLOR_TEXT)
        self.screen.blit(name_text, (x * self.cell_size + 2, y * self.cell_size + self.cell_size + 2))
    
    def draw_ui_panel(self, player: Character, enemies: list[Character], message: str = ""):
        """Draw the UI panel at the bottom (stats, messages, etc)."""
        panel_y = GRID_HEIGHT * self.cell_size
        panel_height = 200
        
        # Background
        pygame.draw.rect(self.screen, (20, 20, 30), (0, panel_y, self.width, panel_height))
        pygame.draw.line(self.screen, COLOR_GRID, (0, panel_y), (self.width, panel_y), width=2)
        
        # Player stats
        y_offset = panel_y + 10
        player_text = f"Player: {player.name} | HP {player.hp}/{player.max_hp} | AC {player.ac} | Level {player.level}"
        text = self.font_small.render(player_text, True, COLOR_TEXT)
        self.screen.blit(text, (10, y_offset))
        
        # Enemy count
        y_offset += 25
        alive_enemies = [e for e in enemies if e.is_alive()]
        enemy_text = f"Enemies: {len(alive_enemies)} alive"
        text = self.font_small.render(enemy_text, True, COLOR_ENEMY)
        self.screen.blit(text, (10, y_offset))
        
        # Message
        if message:
            y_offset += 25
            msg_text = self.font_small.render(message, True, COLOR_SELECTED)
            self.screen.blit(msg_text, (10, y_offset))
    
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen pixel coordinates."""
        return (grid_x * self.cell_size, grid_y * self.cell_size)
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Optional[Tuple[int, int]]:
        """Convert screen pixel coordinates to grid coordinates."""
        grid_y = GRID_HEIGHT * self.cell_size
        if screen_y >= grid_y:
            return None  # Clicked in UI panel
        
        grid_x = screen_x // self.cell_size
        grid_y = screen_y // self.cell_size
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            return (grid_x, grid_y)
        return None
    
    def is_in_keep(self, grid_x: int, grid_y: int) -> bool:
        """Check if a grid position is within the keep."""
        return (
            KEEP_START_X <= grid_x < KEEP_START_X + KEEP_SIZE
            and KEEP_START_Y <= grid_y < KEEP_START_Y + KEEP_SIZE
        )
    
    def render(self, player: Character, player_pos: Tuple[int, int],
               enemies: list, enemy_positions: dict, message: str = ""):
        """Render a frame of the game.
        
        Args:
            player: Player Character
            player_pos: Player (x, y) grid position
            enemies: List of enemy Characters
            enemy_positions: Dict mapping enemy to (x, y) position
            message: Optional message to display
        """
        self.screen.fill(COLOR_BG)
        
        # Draw grid and keep
        self.draw_grid()
        self.draw_keep()
        
        # Draw characters
        self.draw_character(player_pos[0], player_pos[1], player, is_player=True)
        for enemy in enemies:
            if enemy.is_alive() and enemy in enemy_positions:
                pos = enemy_positions[enemy]
                self.draw_character(pos[0], pos[1], enemy, is_player=False)
        
        # Draw UI panel
        self.draw_ui_panel(player, enemies, message)
        
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
    
    def handle_events(self) -> Optional[Tuple[int, int]]:
        """Handle pygame events.
        
        Returns:
            (grid_x, grid_y) if a cell was clicked, None otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    return self.screen_to_grid(event.pos[0], event.pos[1])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        return None
    
    def close(self):
        """Close the pygame window."""
        pygame.quit()
