# Architecture & Design Document

**Date:** 2026-02-22 (Updated: Fog of War + Directional Raids)  
**Status:** Core mechanics formula-based (2024 D&D), GUI framework complete, origin feats live, cover SRD-compliant, fog of war live  
**Python:** 3.11+ for gameplay, 3.14 tests only (no pygame on 3.14)

---

## 🎮 Game Core

### Vision
A tactical roguelike where you defend an 8×8 keep against waves of enemies on a 64×64 grid, using SRD 5.2.1-derived 5.5e combat rules.

### Two Play Modes
1. **Terminal (main.py)** - Full turn-by-turn control, colorized output
2. **Pygame GUI (main_gui.py)** - Visual grid, real-time enemy movement, click-to-play

### Core Gameplay Loop
```
WAVE SPAWNED
    ↓
COMBAT ROUND
  ├─ Initiative rolled (d20 + mod)
  ├─ Each combatant takes turn (by initiative order)
  │   ├─ PLAYER: Choose action (attack/heal/defend/move[GUI only])
  │   └─ ENEMY: Auto-attack or heal
  ├─ Resolve hits (d20 + attack_bonus vs AC)
  ├─ Apply damage or healing
  └─ Check for kills (loot gold, drop items, gain XP)
    ↓
NEXT ROUND (if anyone alive except player)
    ↓
WAVE WON / PLAYER SLAIN
```

---

## 📦 Module Breakdown

### character.py - Core Mechanics
**Class:** `Character`
- **Stats:** `hp, max_hp, ac, attack_bonus, dmg_num, dmg_die, dmg_bonus, initiative_bonus`
- **Ability Scores:** `ability_scores = {STR, DEX, CON, INT, WIS, CHA}` (new in v0.5)
- **Progression:** `level, xp, gold, potions`
- **Optional:** `behavior` (e.g., "healer"), `bounty` (enemy only), `name`

**Ability Score System:**
- Scores range [8-15] using standard array [15, 14, 13, 12, 10, 8]
- Modifiers calculated: `(score - 10) // 2` (2024 D&D formula)
- Example: STR 15 = +2 modifier, CON 14 = +2 modifier, WIS 10 = 0 modifier
- All classes have DEFAULT_ABILITY_SCORES configured in class_definitions.py
- New methods: `get_ability_modifier(ability)`, `get_all_modifiers()`

**Key Methods:**
```python
get_ability_modifier(ability: str) -> int  # Get ability mod (STR, DEX, CON, INT, WIS, CHA)
get_all_modifiers() -> dict                 # Get all 6 modifiers at once
attack(target)              # Roll d20 vs AC, apply damage
defend(ac_bonus=2)          # Increase AC for one round
roll_initiative()           # Roll d20 + init_bonus (+ PB if Alert feat)
use_potion(healing_amount)  # Heal self, consume potion (rolls 2d4+2)
add_xp(amount)              # Check for level up
heal_ally(target, amount)   # Heal another character
has_origin_feat(keyword)    # Check if character has feat matching keyword
_initialize_origin_feats()  # Apply feat effects at creation
_roll_dice_reroll_ones()    # Roll dice, rerolling 1s (Healthy/Iron Fist)
get_buy_cost(base_price)    # Apply Crafty 20% discount if applicable
```

**Origin Feat System:**
All 10 origin feats are applied via `_initialize_origin_feats()` called from `__init__`.
- **Alert:** +PB to initiative in `roll_initiative()`
- **Magic Initiate (Cleric/Druid/Wizard):** Grants cantrips + level-1 spell, free once/long-rest cast, dedicated slot for non-casters. Uses `_get_mi_class()` to extract class. Spellcasting ability set per MI class.
- **Savage Attacker:** Double-roll damage in `attack()`, once per turn (reset in `start_turn()`)
- **Skilled:** +3 skill proficiencies via character creator
- **Crafty:** +3 tool proficiencies via creator, 20% gold discount in `get_buy_cost()`
- **Healthy:** Reroll 1s on healing dice (spells + potions) via `_roll_dice_reroll_ones()`
- **Iron Fist:** Reroll 1s on unarmed strikes via `_roll_dice_reroll_ones()`
- **Meaty:** +2 HP at creation and per level-up

**Mechanics:**
- Attack: `d20 + attack_bonus` vs `target.ac`
- Natural 20: Automatic hit + double damage dice
- Damage: `dmg_num d dmg_die + dmg_bonus`
- Defense: +2 AC for one round (then resets)
- Leveling: XP needed = `100 * current_level`

### class_definitions.py - 2024 D&D Formulas & Class Data
**Purpose:** Verified class definitions from SRD 5.2.1 reference docs.

**Classes:** All 12 SRD classes with hit dies, proficiencies, and calculation formulas

**Key Structures:**
```python
ClassDefinition:
    - name: str (Barbarian, Fighter, Wizard, etc.)
    - hit_die: int (d6, d8, d10, d12)
    - primary_ability: str (STR, DEX, CON, INT, WIS, CHA)
    - saving_throw_proficiencies: list
    - armor_training: str (describes what armor available)
    - weapon_proficiencies: str (Simple, Martial, etc.)
  
DEFAULT_ABILITY_SCORES:
    - One entry per class with standard array [15, 14, 13, 12, 10, 8]
    - Distribution based on class strengths
    - Example: Barbarian = {STR:15, CON:14, WIS:13, DEX:12, INT:10, CHA:8}
```

**Stat Generation Function:**
```python
generate_level_1_stats(class_name, ability_scores=None) -> dict
    Returns: {hp, ac, attack_bonus, dmg_num, dmg_die, dmg_bonus, 
                         initiative_bonus, ability_scores}

    Formulas (2024 D&D):
        HP = (hit_die // 2 + 1) + CON modifier
        AC = Armor base AC + DEX mod (varies: light 11, medium 12, heavy 16)
        Attack Bonus = Ability modifier + proficiency_bonus
        Damage Bonus = Ability modifier (STR for melee)
        Initiative = DEX modifier
```

### dice.py - Utilities
```python
roll_die(sides=20)          # Single die roll: 1 to sides
roll_dice(num, die)         # Multiple rolls: num d die
```

### waves.py - Enemy Spawning
```python
spawn_wave(wave_num)  # Returns list of enemies scaled by wave difficulty
```

**Wave Scaling:**
- Enemy HP: base HP + (5 × wave number)
- Enemy Attack Bonus: base ATB + wave_number
- Enemy Count: 2 + wave number (e.g., Wave 1 = 3 enemies)

### creator.py - Character Creation
**Classes:** 12 presets (Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard)

**Point Buy System:**
- 27 points to distribute
- Base scores: 8
- Range: 8-15
- Cost table: `{8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}`
- Affects: HP (Con), attack (Str), AC (Dex), initiative (Dex)

### items.py - Item System
**Currently:** Potion only
```python
class Item:
    name: str           # "Potion"
    item_type: str      # "potion"
    value: int          # 8 (healing amount)
```

### monsters.py - Enemy Definitions
Pre-defined enemy types (Goblin, Goblin Archer, Champion, Goblin Skulk, etc.)  
**Archetypes:** basic, ranged, tank, healer, sneaky — each with unique behavior and stats

### colors.py - Terminal UI Formatting
**Color Codes:**
- Green: Success, gains (✓)
- Red: Danger, errors (✗)
- Yellow: Warnings (⚠)
- Cyan: Info, headers (ℹ)
- Blue: Player actions
- Magenta: Enemy actions

**Helper Functions:**
```python
success(text)      # Green ✓
error(text)        # Red ✗
warning(text)      # Yellow ⚠
info(text)         # Cyan ℹ
bold(text)         # Bold
header(text)       # Section header
```

---

## 🎯 Terminal Version (main.py)

### Entry Point
```powershell
python main.py [options]
```

**Options:**
- `--interactive, -i` - Prompt for player actions (vs auto-attack)
- `--create-character` - Run character creator first
- `--seed N` - Seed RNG (reproducible runs)
- `--waves N` - Number of waves (default: 3)
- `--no-delay` - Skip 0.4s round delays
- `--single-key` - Single keystroke input (Windows only)

### Combat Loop: `run_combat(player, enemies, interactive=False)`
1. Roll initiative for all combatants
2. Compute final order (with tiebreakers)
3. While player and enemies alive:
   - Each round:
     - By initiative order, each active combatant takes turn
     - Player: Interactive choice OR auto-attack first alive
     - Enemy: Auto-attack player OR heal ally (if healer type)
   - Clear temporary bonuses
   - Display round summary

**Combat Actions (Interactive Mode):**
- `1-9` - Attack enemy (by number)
- `h` - Heal with potion (8 HP)
- `d` - Defend (+2 AC this round)
- `s` - Show stats
- `q` - Quit combat

### Rendering
Terminal-based:
- Enemy list with health bars (`█░`)
- Action menu with clear descriptions
- Color-coded feedback (success/error/info)
- Round summaries
- Player status bar (`[YOUR TURN]`)

---

## 🎨 Pygame GUI Version (main_gui.py + gui.py)

### Architecture
```
main_gui.py
  ├─ GameState          (positions, messages, timers)
  ├─ GameWindow         (rendering, events)
  ├─ Game Loop
  │  ├─ handle_events() (mouse, keyboard)
  │  ├─ move_player()   (click-to-move)
  │  ├─ move_enemies()  (pathfinding to keep)
  │  ├─ resolve_combat()(adjacent hero fights)
  │  └─ render()        (draw frame)
  └─ Wave Loop
```

### Grid System
```
64×64 cells
┌─────────────────────────────────────┐
│  Outer Enemy Spawn Region (56×56)   │
│  ┌─────────────────────────────┐    │
│  │ 8×8 Defended Keep (center)  │    │
│  │  Player spawns here         │    │
│  └─────────────────────────────┘    │
│                                      │
└─────────────────────────────────────┘
```

**Keep Location:**
- X: `(64-8)//2 = 28` to `28+8 = 36`
- Y: `(64-8)//2 = 28` to `28+8 = 36`

### Game State: `GameState`
- `player` - Player character
- `player_pos` - Current (x, y)
- `enemies` - List of enemies
- `enemy_positions` - Dict: enemy → (x, y)
- `selected_target` - Current focus
- `message` - UI message
- `message_timer` - Frames left to display
- `trees` - Set of (x, y) tree positions (Half Cover +2 AC, passable)
- `rocks` - Set of (x, y) rock positions (Three-Quarters Cover +5 AC, blocking)
- `actions_remaining` - Player actions left this turn
- `movement_used` - Movement spent this turn
- `movement_max` - Maximum movement per turn
- `raid_sides` - List of sides enemies raid from (e.g. `['north', 'east']`)
- `_visible_cells` - Set of (x, y) cells currently visible to player (fog of war cache)
- `hidden_enemies` - Set of enemies currently in stealth (invisible to player)
- `_enemy_turn_index` - Index into enemy list during staggered turn processing
- `_processing_subphase` - Sub-state within processing phase: `"idle"` → `"resolving_enemies"` → `"cleanup"`

### Fog of War System
**Vision Range:** `_player_vision_range()` returns cells: base 10 + Perception bonus + darkvision/5

**Visibility:** `compute_player_visibility()` uses Chebyshev distance + Bresenham LOS
- Rocks block line of sight; trees do not
- Called on: init, `move_player()`, Cloud Jaunt teleport, gate passage
- `is_cell_visible(x, y)` — lazy accessor, auto-recomputes if cache is stale

**Rendering:** Dark overlay on non-visible cells; enemies in fog fully hidden

**Targeting:** All attack/spell methods reject fogged targets ("You can't see that area.")
- Exception: Self-centred AoE (e.g. Thunderwave `burst_self`) bypasses fog check

### Raid Direction System
**Spawning:** `add_enemies()` picks 1-3 random sides, always leaving ≥1 free
- Enemies placed within 3 cells of their assigned edge
- Horn blast message generated and displayed at wave start

**Rendering:** Red glow bars along raided edges + directional labels (▼ N, ▲ S, ▶ W, ◀ E)

### Staggered Enemy Turns
Enemy actions resolve one at a time with `pause_frames = 90` (1.5s) between each:
1. `"idle"` → Snapshot positions, move enemies, check AoO triggers
2. `"resolving_enemies"` → `_resolve_single_enemy(enemy)` called per enemy via `_enemy_turn_index`
3. `"cleanup"` → Remove dead enemies from `hidden_enemies`, end round, return to `"player_input"`

### Enemy Stealth System
**Sneaky archetype:** Goblin Skulk (`behavior="sneaky"`) — spawns hidden, attacks with advantage + sneak attack dice, can re-stealth behind rocks.

**Stealth tracking:** `hidden_enemies: set` in GameState. Hidden enemies are invisible in GUI, untargetable by single-target attacks, but hit by AoE.

**Detection:** `_check_player_perception_vs_hidden_enemies()` — Active roll (d20 + Perception bonus) vs enemy stealth total. Called at start of player turn. Silent on failure.

**Re-stealth:** `_enemy_attempt_re_stealth(enemy)` — Requires adjacency to rock (cover). Contested active Perception roll. Silent on failure.

**Attack from stealth:** Sets `_stealth_advantage` flag on Character → advantage ("Unseen Attacker") + sneak attack bonus d6s. Enemy revealed after attacking.

### Cover System
**Method:** `_cover_bonus(attacker_pos, target_pos) -> int`
- Uses Bresenham ray tracing from attacker to target
- For each obstacle adjacent to target, checks dot-product with ray direction
- Only obstacles between attacker and target provide cover (directional)
- Trees = Half Cover (+2 AC), Rocks = Three-Quarters Cover (+5 AC)
- Takes the highest applicable bonus
- Applied to: player melee/ranged attacks, spell attacks, enemy ranged attacks

### Game Window: `GameWindow`
**Rendering Methods:**
```python
draw_grid()                    # Grid lines
draw_keep()                    # Keep area outline + label
draw_character(x, y, char)    # Circle + health bar + name
draw_ui_panel(player, enemies) # Stats panel at bottom
render(player, pos, enemies, positions, message)  # Full frame
```

**Event Handling:**
```python
handle_events()  # Returns clicked (x,y) or None
[ESC or Close]   # Exits game
[Left Click]     # Move if in keep area
```

### Movement & Combat
**Player Movement:** Click within keep area only
- Validates target is within 8×8 keep
- Updates `player_pos`
- Shows confirmatory message

**Enemy Movement:** Pathfinding toward player
- Each frame, move 1 cell closer to player
- Stop if adjacent (distance ≤ 1)
- Clamp to grid bounds

**Combat:** Auto-triggers when adjacent
- Detect if any enemy is within 1 cell (including diagonals)
- Player attacks enemy, enemy counterattacks
- Resolve loot/XP/death
- Display messages to player

### Rendering (60 FPS)
1. Fill background
2. Draw grid lines
3. Draw keep outline
4. Draw all living characters with health bars
5. Draw UI panel with stats/messages
6. Flip display

---

## 🧪 Test Suite

**Framework:** `unittest` (standard library)  
**Files:** `tests/test_*.py`  
**Count:** 230 tests, all passing

### Test Breakdown
| File | Tests | Focus |
|------|-------|-------|
| test_combat.py | 7 | Initiative, attacks, misses, crits |
| test_actions.py | 2 | Defend, heal |
| test_healer.py | 2 | Healing allies |
| test_items.py | 1 | Item drops |
| test_leveling.py | 1 | XP and level-up |
| test_loot.py | 1 | Gold collection |
| test_waves.py | 1 | Wave scaling |

**Run All:**
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

**Sample Test:**
```python
def test_hit_reduces_hp(self):
    attacker = Character("A", hp=10, attack_bonus=5, dmg_die=6, dmg_bonus=1)
    defender = Character("D", hp=10, ac=13)
    random.seed(10)
    
    attacker.attack(defender)
    self.assertEqual(defender.hp, 5)  # Should have taken damage
```

---

## 🔄 Character Creation Flow

### Terminal
```
python main.py --create-character
    ↓
Input name
    ↓
Choose class (1-12)
    ↓
[Optional] Customize ability scores (27-point buy)
    ↓
Character object returned
    ↓
Start combat
```

### GUI
```python
if args.create_character:
    player = create_character_interactive()
else:
    player = Character(...)  # Default fighter
```

---

## 📊 Progression System

### Leveling
**XP Needed:** `100 * current_level`
- Level 1→2: 100 XP
- Level 2→3: 200 XP
- Level 3→4: 300 XP

**On Level Up:**
- `level += 1`
- `max_hp += 5` (heal up to +5 current)
- `attack_bonus += 1`
- Every 2 levels: `ac += 1`

### Loot
**Per Enemy Kill:**
- `gold += enemy.bounty` (typically 3-10)
- 30% chance: `drop Potion` (heal 8 HP)
- `xp += enemy.bounty * 10`

### Gold
- Collected from defeated enemies
- Displayed in UI
- (Future: used for shopping)

---

## 🏗️ Design Philosophy

### Keep It Simple
- D&D 5e spirit, not strict RAW (rules as written)
- Single attack per turn (no multiattack)
- No spellcasting mechanics
- 2-3 action types max

### Make It Playable
- Both terminal & GUI versions work
- No external dependencies except pygame (optional)
- Tests guarantee correctness
- ~15 minutes per wave on average

### Testable & Maintainable
- Clear separation of concerns
- Character system is independent of UI
- Combat is deterministic (seed-able)
- Modular architecture allows easy changes:
  ```python
  # Adding new class is ~10 lines
  # Adding new item type is ~5 lines
  # Adding new enemy is ~5 lines
  ```

---

## ⚠️ Known Limitations & TODOs

### Current Limitations
- No ranged mechanics (all melee)
- Limited enemy behaviors (basic attack, heal, sneaky stealth)
- Simple pathfinding (straight line to player)
- No obstacles or terrain
- No status effects (poison, stun, etc.)

### Future Features (Prioritized)
1. **Class Abilities** - Barbarian rage, Rogue sneak attack, etc.
2. **Ranged Attacks** - Some enemies/players attack from distance
3. **More Enemies** - 20+ enemy types with varied behaviors
4. **Skill Checks** - Dodging, blocking, saves
5. **Equipment** - Weapon/armor system affecting stats
6. **UI Polish** - Animations, sprites, sound effects
7. **Leaderboards** - Track best runs and achievements

---

## 🚀 Getting Started (for next developer/AI)

### Quick Start
```powershell
# 1. Run tests
python -m unittest discover -s tests -p "test_*.py" -v

# 2. Play terminal version
python main.py --interactive --seed 42 --waves 1

# 3. Create custom character
python main.py --create-character --interactive

# 4. Try GUI (Python 3.11 only)
pip install pygame
python main_gui.py --seed 42
```

### Code Entry Points
- **Want to understand combat?** → character.py
- **Want to change wave difficulty?** → waves.py
- **Want to add items?** → items.py
- **Want to modify UI?** → colors.py (terminal) or gui.py (pygame)
- **Want to add enemies?** → monsters.py

### Before Making Changes
1. Read character.py thoroughly
2. Run tests: `python -m unittest`
3. Pick ONE small feature (e.g., "add Poison potion")
4. Implement
5. Add test for it
6. Verify all 15+ tests still pass
7. Commit

---

## 📝 Documentation Files

| File | Purpose |
|------|---------|
| README.md | User guide, how to play |
| CHANGELOG.md | Project state, features, architecture |
| ARCHITECTURE.md | This file - complete design overview |
| GAME_DESIGN.md | Long-term vision and design specification |
| ROADMAP.md | Phased development plan and priorities |
| GIT_COMMIT_GUIDE.txt | How to commit changes |

---

## 🔮 Future Architectural Considerations

**See [GAME_DESIGN.md](GAME_DESIGN.md) for full long-term vision.**

The current architecture (v0.8.1) supports wave-based tactical combat plus early keep/calendar integration. Future phases will require these structural additions:

**Phase 3: Calendar & Time System**
- New module: `calendar.py` - Day/season tracking, raid scheduling
- Extended `character.py` - Exhaustion tracking, rest state management
- New module: `rest_system.py` - Long/short rest logic

**Phase 4: Event System**
- New module: `events.py` - Random event framework and event pool
- New module: `skill_checks.py` - Skill check resolution with DC system
- Event data: `events/` directory with JSON or Python event definitions

**Phase 5: Keep & Territory**
- New module: `keep.py` - Keep structure, upgrades, storage
- New module: `territory.py` - Tile management, resource production
- New module: `builder.py` - Construction system and costs

**Phase 6: Economy & Crafting**
- New module: `economy.py` - Gold, scrap, food tracking
- New module: `crafting.py` - Recipe system, tool proficiency checks
- Extended `items.py` - Expanded item types and crafting recipes

**Phase 7: NPC System**
- New module: `npcs.py` - NPC classes, specialists, management
- New module: `recruitment.py` - Hiring and event-based recruitment
- Extended `combat.py` - Limited NPC combat participation

**Phase 8: Advanced Enemy AI**
- Extended `monsters.py` - Siege behavior, escalation logic
- New module: `siege.py` - Siege equipment mechanics
- Extended map system - Tree line staging area

**Data Structure Considerations:**
- Save/load system will need comprehensive serialization
- Event system requires content pipeline (JSON/YAML recommended)
- NPC system may benefit from inheritance hierarchy
- Resource management needs efficient storage (dict-based inventories)

**Grid System:**
- Current and Future: Traditional 5e grid (characters occupy squares)
- Diagonal movement: Simplified rule (all diagonals = 5 ft) for ease of play
- Alternative variant: 5/10/5 diagonal rule (first diagonal 5 ft, second 10 ft)
- Standard D&D 5e cover and line-of-sight rules apply

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-22 | 0.8.6 | Staggered enemy turns, enemy stealth system (Goblin Skulk), 230 tests |
| 2026-02-22 | 0.8.4 | Fog of war, directional raids, horn blasts, 175 tests |
| 2026-02-20 | 0.8.2 | Origin feats live (10 feats), cover SRD-compliant, 119 tests |
| 2026-02-14 | 0.8.1 | Phase 3 Slice 1 foundation (calendar + keep resource loop) |
| 2026-02-10 | 0.5 | Ability scores, SRD alignment, long-term vision documented |
| 2026-02-08 | 0.2 | Pygame GUI + Enhanced UI |
| Previous | 0.1 | Base game + tests |

---

**Last Updated:** 2026-02-22  
**Maintainer Notes:** This project is well-structured and tested. New developers should read CHANGELOG.md, ARCHITECTURE.md, and GAME_DESIGN.md for full context. Current focus: Phase 3 seasonal-loop baseline completion (Priority 0 in ROADMAP).

