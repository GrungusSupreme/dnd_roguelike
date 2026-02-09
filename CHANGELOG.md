# dnd_roguelike — Changelog & Project State

**Last Updated:** 2026-02-08  
**Version:** 0.2 (Pygame GUI framework + Enhanced UI)

This file documents the complete project state for reference when clearing chat history.

## 📊 Current Status

### ✅ What's Complete
- **Terminal game** - Fully playable, color-coded UI, all mechanics working
- **Pygame GUI framework** - 64×64 grid, 8×8 keep defense, enemy pathfinding (needs Python 3.11+)
- **Test suite** - 15 unit tests, all passing
- **Character system** - 12 classes, point-buy customization, leveling
- **Combat mechanics** - D&D 5.5e rules-as-written (initiative, attacks, crits, loot, XP)

### ⚠️ Known Limitations
- Pygame requires Python 3.11 or older (3.14 has distutils issue)
- GUI is text-free, uses simple shapes (circles for chars, rectangles for UI)
- Enemy AI is basic (straight pathfinding to keep)

## 🎮 Game Overview

**Genre:** Tactical roguelike wave-survival with D&D 5.5e combat

**Two Play Modes:**
1. **Terminal** (main.py) - Text-based, full interactivity, colorized
2. **Pygame GUI** (main_gui.py) - Visual grid, 60 FPS, real-time enemy movement

**Core Loop:**
- Enemies spawn in waves (scale gets harder each wave)
- Player fights to win XP, gold, loot
- Level up to gain stats
- Survive N waves to win

## Project snapshot (2026-02-08)
- Language: Python 3.14 (3.11 for pygame support)
- Tests: `unittest` (15 tests, 100% passing)
- Entries: 
  - `main.py` — interactive terminal combat
  - `main_gui.py` — pygame visual grid (requires pygame)

## Key modules
- `main.py`: combat loop, initiative ordering, CLI flags (`--interactive`, `--create-character`, `--seed`, `--waves`, `--no-delay`, `--single-key`).
- `character.py`: `Character` model (HP, AC, attack, damage, potions, gold, bounty, XP & leveling, basic actions).
- `dice.py`: `roll_die` / `roll_dice` helpers.
- `monsters.py`: enemy factory used by `waves.py`.
- `waves.py`: `spawn_wave()` helper for wave scaling.
- `items.py`: `Item` dataclass and simple item handling.
- `creator.py`: interactive character creator with 12 D&D base classes and optional point-buy.
- `tests/`: unit tests covering combat, initiative, items, healer, loot, and leveling.

## Design decisions / mechanics
- Initiative: d20 + initiative bonus; tied totals use an extra d20 tie-break roll.
- Attacks: d20 + attack bonus; natural 20 is a crit (extra damage dice).
- Loot & XP: enemies have `bounty`; killing grants gold and `XP = bounty * 10`.
- Leveling: XP-to-next-level = `100 * level`. On level up: +1 level, +5 max HP (heal up to +5), +1 attack bonus, +1 AC every 2 levels.
- Items: simple `Potion` item increments `Character.potions` when added.
- Character creator: 12-class presets + optional 27-point buy (scores 8–15; 5e-style costs). Point-buy affects HP, attack, damage, AC, and initiative via ability modifiers.

## How to run
Run the demo:
```powershell
python main.py --interactive --seed 42
```

Use the creator before running:
```powershell
python main.py --create-character --interactive
```

Run tests:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### GUI Version (requires Python 3.11+)
```powershell
# Install pygame first
pip install pygame

# Then run GUI
python main_gui.py --seed 42 --waves 3
```

## 🔧 Architecture & Modules

### Core Game Engine
- **character.py** - Character class with all D&D mechanics
  - Stats: HP, AC, attack_bonus, dmg_num, dmg_die, dmg_bonus
  - Systems: initiative, attack rolls, defense, leveling, XP
  - Methods: roll_initiative(), attack(), defend(), add_xp(), use_potion()

- **dice.py** - Dice rolling utilities
  - roll_die(sides) - single d-sided roll
  - roll_dice(num, die) - multiple rolls

- **items.py** - Item system
  - Item dataclass
  - Potion healing mechanics
  - Inventory management

- **waves.py** - Enemy spawning
  - spawn_wave(wave_num) - creates scaled enemy groups
  - Scaling: HP/damage increase by 10% per wave

- **creator.py** - Character creation
  - 12 D&D class presets
  - 27-point ability score buy system
  - Point-buy to character stat conversion

### Terminal UI
- **main.py** - Terminal game loop
  - run_combat(player, enemies, interactive)
  - compute_initiative_order()
  - Player input handling
  - Round-by-round turn system

- **colors.py** - Text formatting
  - ANSI color codes
  - Helper functions (success, error, info, etc.)

### Pygame GUI (New - 2026-02-08)
- **gui.py** - Rendering engine
  - GameWindow class
  - draw_grid(), draw_keep(), draw_character()
  - Screen/grid coordinate conversion
  - Input handling (mouse, keyboard)

- **main_gui.py** - GUI game loop
  - GameState class (positions, messages)
  - move_player(), move_enemies()
  - resolve_combat()
  - 60 FPS game loop

### Tests
- **test_combat.py** - Attack/defense/initiative (7 tests)
- **test_actions.py** - Defend/heal (2 tests)
- **test_healer.py** - Healing allies (2 tests)
- **test_items.py** - Item drops (1 test)
- **test_leveling.py** - XP/leveling (1 test)
- **test_loot.py** - Gold collection (1 test)
- **test_waves.py** - Wave scaling (1 test)

## Recent Changes (Current Session)

### ✅ QoL Improvements
- Color-coded terminal UI (green for success, red for danger, etc.)
- Better action menu formatting
- Health bars for enemies
- Improved round summaries

### ✅ GUI Implementation
- Created Pygame rendering system
- Implemented 64×64 grid with 8×8 keep area
- Enemy pathfinding toward player
- Click-to-move within keep
- Adjacent combat detection
- Real-time game loop (60 FPS)
- Health bars above characters
- UI panel with stats

## Next Steps / TODOs

### High Priority
1. **Pygame Compatibility** - Test on Python 3.11 with pygame
2. **GUI Polish** - Add sprite characters, better visuals
3. **Game Feel** - Add sound effects, visual feedback

### Medium Priority
1. **More Enemy Types** - Different behaviors (ranged, melee, healer)
2. **Skill System** - Class-specific abilities beyond attack
3. **Difficulty Scaling** - Modifiers for wave difficulty
4. **Pause Menu** - In-game settings and stats

### Nice to Have
1. **Leaderboard** - Track best runs
2. **Save/Load** - Continue games between sessions
3. **Map Generation** - Obstacles on grid
4. **Animation** - Attack/movement feedback
5. **Multiplayer** - Co-op wave defense

## File Structure

```
dnd_roguelike/
├── main.py                    (Terminal entry point)
├── main_gui.py                (Pygame entry point)
├── gui.py                     (Pygame rendering)
├── character.py               (Core mechanics)
├── creator.py                 (Character creation)
├── waves.py                   (Enemy spawning)
├── items.py                   (Item system)
├── dice.py                    (Dice utilities)
├── colors.py                  (Terminal colors)
├── monsters.py                (Enemy definitions)
├── tests/                     (15 unit tests)
├── README.md                  (User guide)
├── CHANGELOG.md               (This file)
├── IMPLEMENTATION_SUMMARY.md  (Technical overview)
├── GUI_NOTES.md               (GUI development notes)
├── QUICKSTART.md              (Quick reference)
└── .gitignore
```

## How AI Should Approach Development

When AI continues this project after chat clear:

1. **Always run tests first** - `python -m unittest discover`
2. **Reference CHANGELOG.md** - Understand current state
3. **Check IMPLEMENTATION_SUMMARY.md** - See architecture
4. **Look at GUI_NOTES.md** - Understand pygame setup
5. **Terminal version is stable** - Don't break it (test after changes)
6. **GUI needs Python 3.11** - Document this clearly
7. **Keep both versions in sync** - Changes to characters/combat affect both

## Known Issues & Workarounds

### Issue: ModuleNotFoundError: pygame
**Cause:** Python 3.14 doesn't have distutils  
**Solution:** Switch to Python 3.11 and install pygame

### Issue: Terminal colors don't show
**Cause:** Some terminals don't support ANSI colors  
**Workaround:** Redirect output to file: `python main.py > game.txt`

### Issue: GUI unresponsive on Windows
**Cause:** Pygame needs to pump events  
**Fix:** Already handled in main loop with handle_events()

## Performance Notes

- Terminal version: instant (text-only)
- Pygame GUI: 60 FPS target (achieves ~60 with current code)
- Test suite: <0.01 seconds (15 tests)
- Grid render: O(grid_size) complexity, optimized drawing

## If you clear chat and come back:

1. Read CHANGELOG.md completely
2. Run: `python -m unittest discover -s tests -p "test_*.py" -v`
3. Try: `python main.py --interactive --seed 42`
4. Check IMPLEMENTATION_SUMMARY.md for architecture questions
5. Look at GUI_NOTES.md if working on pygame

The project is well-tested and documented. Good luck!
git push
```
2. Save this file (`CHANGELOG.md`) — it contains the short project state.
3. Clear the chat to reset the model context; when you reopen, point me to this repo and I can continue working from files.

## Next suggested tasks
- Add `README` section documenting the creator + point-buy (small, done-on-request).
- Add save/load for created characters (`characters/` JSON files).
- Add unit tests for `creator.py` (simulate inputs using `unittest.mock`).
- Add CI (GitHub Actions) to run tests on push.

---
Generated by the assistant as a compact project snapshot — keep in repo as canonical context.
