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

**Character Creation (D&D 2024 Rules):**
- **Point Buy System:** 27 points, ability scores 8-15 (standard D&D costs)
- **16 Backgrounds:** Each provides origin feat, skill proficiencies, and ability score increases
- **Background ASI:** Choose +2/+1 split or +1/+1/+1 to three suggested abilities
- **9 Species:** Dragonborn, Dwarf, Elf, Gnome, Goliath, Halfling, Human, Orc, Tiefling
- **HP Calculation:** Full hit die + CON modifier at level 1 (SRD-compliant)

**Spellcasting (Combat-Focused):**
- Class-based cantrip/level-1 spell selection at character creation
- Spell slots tracked and displayed in combat UI
- AoE spell casting with live cursor preview

**Species Traits (Combat-Relevant):**
- Dragonborn Breath Weapon + ancestry resistance
- Tiefling/Elf/Gnome lineage or legacy magic support
- Gnome mental-save advantage, Halfling Lucky rerolls
- Orc Relentless Endurance + Adrenaline Rush, Goliath ancestry actions

**Tactical Combat:**
- **Cover System:** Trees (provide cover, passable) and Rocks (provide cover, block movement/LOS)
- Both give +2 AC when adjacent
- Obstacles span entire map with 6-block gap around keep

## Rules References

This project uses the local SRD 5.2.1 reference docs as the only rules source:
- RULES_REFERENCE.md
- CLASS_REFERENCE.md
- SPECIES_REFERENCE.md
- FEATS_REFERENCE.md
- EQUIPMENT_REFERENCE.md
- SPELLS_REFERENCE.md
- MAGIC_ITEMS_REFERENCE.md
- MONSTERS_REFERENCE.md

Apply these rules consistently across the project and avoid external sources to reduce copyright risk.

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

## Multi-Agent Workflow (No-Code)

If you want to run this project without writing code, use the built-in multi-agent kit:

- `AGENT_OPERATIONS.md` - roles, rules, cadence, and definition of done
- `AGENT_PROMPTS.md` - copy/paste prompts for Builder, Reviewer, QA/Balance, and orchestrated sessions

Recommended workflow:
1. Fill a Task Card from `AGENT_OPERATIONS.md`
2. Run Builder prompt from `AGENT_PROMPTS.md`
3. Run Reviewer prompt
4. Run Builder fix pass
5. (Optional) Run QA/Balance prompt

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
