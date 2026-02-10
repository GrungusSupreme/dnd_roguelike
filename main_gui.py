"""Pygame-based main loop for the D&D roguelike.

Replaces the terminal version with a visual battle grid.
"""
import random
import argparse
from character import Character
from creator import create_character_interactive
from character_creator_gui import create_character_gui
from waves import spawn_wave
from gui import GameWindow, KEEP_START_X, KEEP_START_Y, KEEP_SIZE, GRID_WIDTH, GRID_HEIGHT
import dice
import math


class GameState:
    """Manages game state including character positions."""
    
    def __init__(self, player: Character):
        self.player = player
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
        
    def add_enemies(self, enemies: list):
        """Add enemies and place them on the grid (outer regions)."""
        self.enemies = enemies
        for enemy in enemies:
            # Spawn enemies on the outer edges
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            # Keep trying until we get a position outside the keep
            while (KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE and
                   KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE):
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
            self.enemy_positions[enemy] = (x, y)
    
    def move_player(self, target_x: int, target_y: int) -> bool:
        """Move player to target position on grid. Return True if moved."""
        # Clamp to grid bounds
        target_x = max(0, min(GRID_WIDTH - 1, target_x))
        target_y = max(0, min(GRID_HEIGHT - 1, target_y))
        
        self.player_pos = (target_x, target_y)
        self.message = f"Moved to ({target_x}, {target_y})"
        self.message_timer = 20
        return True
    
    def move_enemies(self):
        """Move enemies toward the player (within keep area)."""
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            if enemy not in self.enemy_positions:
                continue
            
            ex, ey = self.enemy_positions[enemy]
            px, py = self.player_pos
            
            # Simple pathfinding: move toward player
            dx = px - ex
            dy = py - ey
            
            # Don't move if adjacent or on player
            if abs(dx) <= 1 and abs(dy) <= 1:
                continue
            
            # Move one step closer
            new_x = ex + (1 if dx > 0 else -1 if dx < 0 else 0)
            new_y = ey + (1 if dy > 0 else -1 if dy < 0 else 0)
            
            # Clamp to grid
            new_x = max(0, min(GRID_WIDTH - 1, new_x))
            new_y = max(0, min(GRID_HEIGHT - 1, new_y))
            
            self.enemy_positions[enemy] = (new_x, new_y)
    
    def resolve_combat(self):
        """Check for adjacent enemies and resolve combat."""
        px, py = self.player_pos
        
        for enemy in self.enemies:
            if not enemy.is_alive():
                continue
            
            if enemy not in self.enemy_positions:
                continue
            
            ex, ey = self.enemy_positions[enemy]
            
            # Check if adjacent (within 1 cell, including diagonals)
            if abs(ex - px) <= 1 and abs(ey - py) <= 1 and (ex != px or ey != py):
                # Combat!
                self.player.attack(enemy)
                if not enemy.is_alive():
                    # Loot
                    self.player.gold += enemy.bounty
                    self.message = f"Defeated {enemy.name}! Looted {enemy.bounty} gold."
                    self.message_timer = 40
                    xp_gain = enemy.bounty * 10
                    self.player.add_xp(xp_gain)
                else:
                    self.message = f"Hit {enemy.name} for some damage!"
                    self.message_timer = 30
                
                # Enemy counterattack
                if enemy.is_alive():
                    enemy.attack(self.player)
                    if not self.player.is_alive():
                        self.message = "You have been slain!"
                        self.message_timer = 60
    
    def update(self, window: GameWindow):
        """Update game state each frame."""
        if self.pause_frames > 0:
            self.pause_frames -= 1
            if self.message_timer > 0:
                self.message_timer -= 1
            return
        
        if self.turn_phase == "player_input":
            self.message = ">>> Your turn! Click to move within the keep <<<"
            self.message_timer = 999
            # Waiting for player input (handled in main loop)
            return
        
        if self.turn_phase == "processing":
            # Move enemies
            self.move_enemies()
            self.pause_frames = 30  # Show movement for 0.5 seconds
            
            # Resolve combat
            self.resolve_combat()
            
            # Switch back to player input
            self.turn_phase = "player_input"
            self.pause_frames = 30
        
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
        player = Character(
            "Hero",
            hp=30,
            ac=15,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=8,
            dmg_bonus=3,
            initiative_bonus=2,
        )
    elif args.create_character and args.terminal_creator:
        # Terminal-based creator
        player = create_character_interactive()
    else:
        # Default: GUI character creator
        player = create_character_gui()
    
    # Initialize window
    window = GameWindow(cell_size=12)
    
    try:
        # Wave loop
        for wave in range(1, args.waves + 1):
            if not window.running:
                break
            
            # Spawn wave
            enemies = spawn_wave(wave)
            state = GameState(player)
            state.add_enemies(enemies)
            state.message = f"Wave {wave}! Defend the keep!"
            state.message_timer = 60
            
            # Battle loop
            while window.running and player.is_alive() and any(e.is_alive() for e in enemies):
                # Handle input
                clicked = window.handle_events()
                if clicked and state.turn_phase == "player_input":
                    if state.move_player(clicked[0], clicked[1]):
                        state.turn_phase = "processing"
                        state.round_number += 1
                
                # Update game state
                state.update(window)
                
                # Render
                window.render(player, state.player_pos, enemies, state.enemy_positions, state.message)
            
            if not player.is_alive():
                print(f"Game Over! Survived {wave - 1} waves.")
                break
        else:
            print(f"Victory! Survived all {args.waves} waves.")
    
    finally:
        window.close()


if __name__ == "__main__":
    main()
