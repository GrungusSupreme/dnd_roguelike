# dnd_roguelike

DND 5.5e video game with full class features, items, spells and actions. Waves of enemies assault the position and you defeat them to level up and get gold to buy items or upgrade physical defenses. The game is played on a simple grid map with minimal graphic assets and focuses on mimicking DnD 5.5e combat as close to rules-as-written as possible.

Minimal hobby roguelike combat simulator (terminal) — start of a D&D-inspired wave-survival project.

Current files
- `main.py`: simple combat demo with `Character`, `roll_die`, and `roll_dice`.

Run the demo

```powershell
python main.py
```

Interactive play

Start the demo interactively to choose targets each turn:

```powershell
python main.py
# then respond 'y' when prompted "Play interactively? (y/N):"
```

Controls during interactive combat:
- Enter the enemy number to attack that enemy.
- Enter `s` to show player stats.
- Enter `q` to quit the combat.

CLI options

- `--interactive, -i`: prompt for choices each player turn (same as interactive prompt)
- `--single-key`: use single-key input (Windows only, uses `msvcrt.getwch` so no Enter required)
- `--seed <n>`: seed RNG for reproducible runs (e.g., `--seed 42`)
- `--waves <n>`: run a specific number of waves (default 3)

Examples

```powershell
python main.py --interactive --single-key --seed 42 --waves 5
python main.py --seed 123
```

No-delay (fast testing)

Use `--no-delay` to skip the short pause between rounds, useful for fast manual testing or when running many waves:

```powershell
python main.py --no-delay
```

Loot and gold

Enemies drop a small `bounty` when defeated. The player's gold is tracked on the `Character` and printed when looting enemies.

Items and inventory

- Enemies can drop items (currently `Potion`) with a small chance. Collected items are stored on the player's `inventory` and may affect `potions` count.
- Use potions during combat with the `h` action (heal).

XP and Leveling

- Enemies award XP when defeated (simple formula: `bounty * 10`).
- Players gain levels when reaching XP thresholds (`100 * level`), which increases `max_hp`, `attack_bonus`, and sometimes `AC`.

Leveling details

- XP curve: you need `100 * current_level` XP to reach the next level.
- On level up: `level` increments by 1, `max_hp` increases by 5 (and you heal up to +5), `attack_bonus` increases by 1, and every 2 levels your `AC` increases by 1.
- XP is granted automatically when an enemy with a `bounty` is killed during `run_combat`.

Character Creator & Point-Buy

- Start the interactive character creator before running the demo:

```powershell
python main.py --create-character --interactive
```

- The creator presents 12 base classes (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard) as presets.
- After choosing a class you can optionally customize ability scores using a 27-point buy (scores start at 8, min 8, max 15). Costs follow the standard 5e-like table: `{8:0,9:1,10:2,11:3,12:4,13:5,14:7,15:9}`.
- Point-buy affects the created `Character` by applying simple ability modifiers: Con modifies HP, Str modifies attack and damage, Dex modifies initiative and AC, etc. This is intentionally lightweight for the roguelike demo.

Notes
- The creator is interactive in-terminal and intended for local play. If you want non-interactive creation (for tests or automation) I can add a CLI flag to pass a JSON file describing the character.




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
