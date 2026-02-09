#!/usr/bin/env python3
"""
Quick demo script: Runs combat directly with a pre-made character.
This shows what interactive combat looks like without the creator prompts.
"""
from character import Character
from waves import spawn_wave
from main import run_combat

# Create a custom character (example: Fighter)
player = Character(
    name="Thora the Fighter",
    hp=34,
    ac=16,
    attack_bonus=6,
    dmg_num=1,
    dmg_die=8,
    dmg_bonus=3,
    initiative_bonus=1,
    potions=2,
)

print("="*60)
print("INTERACTIVE COMBAT DEMO")
print("="*60)
print(f"Character: {player.name}")
print(f"HP: {player.max_hp} | AC: {player.ac} | Attack: +{player.attack_bonus}")
print(f"Potions: {player.potions}")
print("="*60)

# Run wave 1
for wave in range(1, 2):
    print(f"\n{'═'*50}")
    print(f"  WAVE {wave}")
    print(f"{'═'*50}\n")
    
    enemies = spawn_wave(wave)
    print(f"Enemies spawned: {', '.join(e.name for e in enemies)}\n")
    
    survived = run_combat(player, enemies, interactive=True)
    
    if not survived:
        print(f"\nGame Over - You survived {wave-1} waves.")
        break
else:
    print(f"\n🏆 VICTORY! Waves cleared!")
    print(f"Final Stats - HP: {player.hp}/{player.max_hp} | Gold: {player.gold} | XP: {player.xp}")
