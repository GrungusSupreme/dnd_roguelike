# dnd_roguelike

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
