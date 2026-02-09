# dnd_roguelike

DND 5.5e video game with full class features, items, spells and actions. Waves of enemies assault the position and you defend a central **8x8 keep** on a larger **64x64 battle grid**. Enemies advance from the outer regions, and you position yourself tactically to defeat them. The game focuses on mimicking D&D 5.5e combat as close to rules-as-written as possible.

Pygame-based tactical roguelike with wave-survival mechanics.

## Quick Start

### GUI Version (Recommended)

```powershell
python main_gui.py
```

This launches the graphical battle grid. Click anywhere within the keep (green area) to move, and automatically attack adjacent enemies.

**Controls:**
- **Left Click**: Move to that position within the keep
- **ESC or Close Window**: Exit game

### Interactive Terminal Version

```powershell
python main.py --interactive
```

Text-based version with full command input each turn.

**Options for `main.py`:**
- `--interactive, -i`: prompt for choices each player turn
- `--create-character`: run character creator before starting
- `--single-key`: Windows only, single-key input (no Enter required)
- `--seed <n>`: seed RNG for reproducible runs
- `--waves <n>`: number of waves (default 3)
- `--no-delay`: skip delays between rounds

**Terminal Controls:**
- `1-9`: Attack enemy number
- `h`: Heal with potion
- `d`: Defend (+2 AC)
- `s`: Show stats
- `q`: Quit

## Battle Grid System

**Grid Layout:**
- **64x64** total battle area
- **8x8 keep** (green-highlighted) - defended position in the center
- **Outer regions** - where enemies spawn and advance from

**Mechanics:**
- Player can only move within the 8x8 keep
- Enemies automatically move toward the keep
- Adjacent enemies (within 1 cell) auto-attack
- Positioning affects defense and survival## Requirements

- Python 3.10+
- `pygame` (for GUI version)

Install dependencies:
```powershell
pip install pygame
```

## Features

**Core Mechanics:**
- Full D&D 5.5e initiative system (d20 + modifier, tiebreakers)
- Attack rolls with natural 20 criticals (double damage dice)
- Armor class (AC) system with defense actions
- Health points and leveling

**Progression:**
- Enemies award XP on defeat: `bounty * 10`
- Level up when reaching `100 * level` XP
- Each level: +5 max HP, +1 attack bonus, +1 AC every 2 levels
- Gold collected from enemy bounties

**Items & Abilities:**
- Healing potions (8 HP restore)
- Chance to loot items from defeated enemies
- Defend action: +2 AC for one round

**Character Classes:**
12 playable classes with presets: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard

**Character Customization:**
Ability score point-buy system (27 points, range 8-15, standard D&D 5e costs)

## Testing

Run unit tests:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

All 15 tests verify combat mechanics, leveling, loot, and wave scaling.

## Project Structure

```
main_gui.py          - Pygame GUI entry point
gui.py              - Pygame window and rendering
main.py             - Terminal version entry point  
character.py        - Character class and combat
creator.py          - Character creator with point-buy
waves.py            - Enemy wave spawning & scaling
items.py            - Item system
dice.py             - Dice rolling utilities
colors.py           - Terminal color formatting
tests/              - Unit tests
```

## Development Notes

The GUI version features:
- **64x64 grid** with visual rendering
- **8x8 keep** (defend this region)
- **Tactical positioning** - click to move within keep
- **Auto-combat** when adjacent to enemies
- Real-time enemy movement toward keep

Terminal version retains:
- Full interactive turn-by-turn control
- Character customization
- Reproducible runs with `--seed`
- Color-coded feedback




Run tests

```powershell
python -m unittest discover -v
```

Next steps
- Split logic into `dice.py` and `character.py`.
- Add initiative, multiple enemies, and waves.

Recent additions
- Initiative system and multi-enemy demo in `main.py`.
- Tests updated to include initiative ordering.

Wave system
- `waves.py` contains a simple `spawn_wave(wave_number)` helper that returns a list of enemies with basic scaling (HP and attack).
- The demo now runs multiple waves in `main.py`.
