# dnd_roguelike — Changelog & Project State

**Last Updated:** 2026-02-22 (Session 16 - Staggered Enemy Turns + Enemy Stealth System)  
**Version:** 0.8.6 (Staggered Combat + Goblin Skulk Stealth)

This file documents the current project state for reference when clearing chat history.

---

## 📋 Session 16 - Staggered Enemy Turns + Enemy Stealth System

### ✅ COMPLETED THIS SESSION

#### Staggered Enemy Turns (main_gui.py — GameState)
Previously, all enemies resolved their actions in a single `resolve_combat()` pass within one frame, making combat feel instant. Now each enemy acts one at a time with a visible 1.5-second pause between turns.

**Core mechanism:**
- `_enemy_turn_index: int` — Tracks which enemy is currently acting during the processing phase
- `_processing_subphase` expanded from `"idle"` / `"post_movement"` to include `"resolving_enemies"` and `"cleanup"`
- Phase flow: `"idle"` → snapshot + move + AoO checks → `"resolving_enemies"` → process one enemy per update cycle → `"cleanup"` → end round → `"player_input"`
- `_resolve_single_enemy(enemy)` — Extracted from old `resolve_combat()` loop body. Handles adjacency check, attack roll, damage, healing behavior, and stealth mechanics for one enemy.
- `self.pause_frames = 90` (1.5s at 60 FPS) set after each enemy acts, creating visible gaps between enemy turns
- Enemy list iterated via `_enemy_turn_index`; increments after each enemy resolves or is skipped (dead/not adjacent)

#### Enemy Stealth System — Goblin Skulk Archetype
A new `"sneaky"` enemy archetype that can enter stealth, attack from hiding with advantage and bonus sneak attack damage, and be detected by the player's active Perception checks.

**New archetype in monsters.py:**
- `"sneaky"` archetype creates **Goblin Skulk**: AC 13, HP 7 + wave scaling, +5 attack, 1d4+2 damage, range 3
- `behavior = "sneaky"` — Flags the enemy for stealth behavior
- `stealth_bonus = 6 + wave_scaling_attack` — Used for contested stealth checks
- `sneak_attack_dice = 1 + (wave - 1) // 3` — Extra d6s of damage when attacking from stealth (scales with wave)
- Added to wave 3+ archetype rotation in `waves.py`
- Dark green color `(100, 140, 100)` in gui.py for skulk rendering

**Stealth tracking in GameState:**
- `hidden_enemies: set` — Tracks which enemies are currently stealthed
- Populated in `add_enemies()` for enemies with `behavior="sneaky"`
- Cleaned up in `"cleanup"` subphase (dead enemies removed from set)

**Stealth attack mechanics (in `_resolve_single_enemy`):**
- When a hidden enemy attacks, it sets `player._stealth_advantage = True` → grants advantage ("Unseen Attacker") on the attack roll via `character.py`'s `attack()` advantage_reasons list
- Rolls `sneak_attack_dice` × d6 bonus damage on hit
- Enemy is **revealed** after attacking (removed from `hidden_enemies`) regardless of hit/miss
- Combat log shows "[Enemy] strikes from the shadows!" and sneak attack damage separately

**Player Perception checks:**
- `_check_player_perception_vs_hidden_enemies()` — Called at start of each player turn
- **Active roll:** `d20 + Perception bonus` vs enemy's `stealth_bonus + 10` (stealth total)
- On success: enemy revealed, message "[Enemy] spotted! (Perception [roll] vs Stealth [DC])"
- On failure: **silent** — no message shown, player doesn't know a check was made
- `_player_can_attempt_detection()` — Returns True (one check per turn)

**Re-stealth mechanic:**
- `_enemy_attempt_re_stealth(enemy)` — Called after a sneaky enemy's turn if it's not hidden
- Requires enemy to be adjacent to a rock (cover)
- Contested: enemy `stealth_bonus + d20` vs player's active `d20 + Perception bonus`
- On success: enemy re-enters `hidden_enemies`, message "[Enemy] slips back into the shadows!"
- On failure: **silent** — no message shown

**AoE interaction:**
- `cast_aoe_spell_at()` now includes hidden enemies in its target list
- Hidden enemies hit by AoE are **revealed** ("flushed out of hiding by the blast!")
- Single-target attacks (`attack_enemy_at()`) and spells (`cast_spell_at()`) still skip hidden enemies — player cannot target what they can't see

**GUI rendering:**
- `render()` accepts `hidden_enemies` parameter
- Enemy rendering loop skips enemies in `hidden_enemies` — they are invisible on the grid
- No health bar, no name, no circle — fully hidden until revealed

### 🧪 Test Coverage
- **23 new tests** in `tests/test_enemy_stealth.py`:
  - `TestSneakyEnemySpawnHidden` (3 tests): sneaky enemy starts hidden, non-sneaky doesn't, hidden set populated on spawn
  - `TestPlayerPerceptionCheck` (4 tests): successful detection reveals, failed detection is silent, active roll uses d20+bonus, detection at turn start
  - `TestSneakyEnemyAttack` (4 tests): attack from stealth has advantage, sneak attack adds bonus d6 damage, enemy revealed after attack, attack message shows stealth flavor
  - `TestSneakyEnemyReStealth` (3 tests): re-stealth near rock succeeds on high roll, fails without cover, contested by active Perception
  - `TestPlayerCannotTargetHidden` (1 test): click-to-attack skips hidden enemies
  - `TestAoEHitsHiddenEnemies` (1 test): AoE includes and reveals hidden enemies
  - `TestMakeEnemySneaky` (4 tests): sneaky archetype stats, stealth_bonus scaling, sneak_attack_dice scaling, behavior flag
  - `TestCharacterStealthAdvantage` (2 tests): _stealth_advantage grants advantage, flag auto-clears after attack
  - `TestCleanupDeadHidden` (1 test): dead enemies removed from hidden_enemies set
- **Total test count: 230 (207 existing + 23 new), all passing**

### 🔧 Architecture Impact
- **No breaking changes** to existing systems
- `_resolve_single_enemy()` replaces the inner loop body of old `resolve_combat()` — same logic, now called per-enemy with pauses
- `hidden_enemies` set is a new GameState field — all existing code paths are unaffected (enemies not in the set behave normally)
- `character.py` change is minimal: `_stealth_advantage` flag checked in existing `advantage_reasons` list, auto-clears after use
- Trigger system from Session 15 is fully compatible — triggers still queue during staggered enemy turns
- Fog of war and stealth are independent systems: fog hides based on player vision range, stealth hides based on enemy behavior

### 📌 Resume Notes
- The `"sneaky"` archetype is the first enemy with behavior-driven combat mechanics beyond basic attack/heal
- Enemy stealth mirrors the player's Hide system conceptually (contested Stealth vs Perception) but uses its own implementation in GameState rather than character.py
- `_stealth_advantage` on Character is a generic flag — any future "unseen attacker" mechanic can set it
- Staggered turns make future per-enemy visual effects feasible (animations, status icons, etc.)
- Re-stealth requires adjacency to a rock — this creates tactical play where destroying/avoiding cover matters
- Silent failure on Perception checks prevents metagaming — player doesn't know hidden enemies exist until revealed
- `_processing_subphase` states: `"idle"` → `"resolving_enemies"` → `"cleanup"` — future enemy phases can be inserted
- Phase 3 seasonal loop remains the next major milestone

---

## 📋 Session 15 - Mid-Combat Trigger Confirmation System

### ✅ COMPLETED THIS SESSION

#### Trigger Queue System (main_gui.py — GameState)
Previously, weapon masteries (Push/Cleave/Nick) auto-applied on hit, on-hit species features (Goliath ancestry) used sidebar buttons, and Attack of Opportunity didn't exist. Now all optional mid-combat decisions use a **unified trigger queue** with modal confirmation popups.

**Core mechanism:**
- `pending_triggers: list[dict]` — FIFO queue of trigger dicts with title, description lines, accept/decline labels, and callback functions
- `queue_trigger(trigger)` — Adds a trigger to the queue
- `get_current_trigger_modal()` — Returns a modal dict for the front trigger (compatible with existing `draw_modal_overlay()`)
- `resolve_current_trigger(accepted)` — Pops the front trigger, calls on_accept or on_decline callback
- New turn phase `"awaiting_trigger"` — Pauses combat while waiting for player response. All other clicks are ignored.
- `_trigger_resume_phase: str` — Remembers which phase to return to after all triggers are resolved (player_input or processing)

#### Attack of Opportunity (Reaction Economy)
- **New state:** `reaction_used: bool` — One reaction per round, resets at start of player turn
- **Detection:** `_check_aoo_triggers(pre_move_positions)` — Called after `move_enemies()` with a snapshot of enemy positions from before movement. If any enemy moved from within player melee reach to outside reach, queues an AoO trigger.
- **Melee reach calculation:** `_get_player_melee_reach()` returns 1 tile (5 ft) normally, 2 tiles (10 ft) for Reach weapons. `_player_has_melee_capability()` returns False for ranged-only weapons.
- **AoO modal:** "Attack of Opportunity — [Enemy] is leaving your reach! Spend your reaction to make a melee attack?" Accept rolls a melee attack and sets `reaction_used = True`. Only one AoO queued per round.

#### Weapon Mastery Confirmations (Push / Cleave / Nick)
Previously auto-applied on hit. Now `_queue_weapon_mastery_trigger(enemy, mastery)` queues a modal:
- **Push:** "Shove the target 1 tile away?" → calls `_apply_push_mastery()` on accept
- **Cleave:** "Deal weapon damage to an adjacent enemy?" — Only queued if valid secondary targets exist near the primary target. Shows candidate names. → calls `_apply_cleave_mastery()` on accept
- **Nick:** "Make an extra offhand attack with [weapon]?" — Only queued if a Light offhand weapon is equipped. → calls `_apply_nick_mastery()` on accept

**Phase transition:** After `attack_enemy_at()`, if triggers were queued, `turn_phase` changes to `"awaiting_trigger"` with `_trigger_resume_phase = "player_input"`.

#### On-Hit Species Feature Triggers (Goliath Ancestry)
- `_queue_on_hit_species_triggers(enemy)` — Replaces the old `_set_pending_on_hit_options()` + sidebar button approach
- Goliath Fire's Burn, Frost's Chill, Hill's Tumble now use modal confirmation popups
- Old `pending_on_hit_actions` dict and `get_pending_on_hit_ui_actions()` still exist but are no longer populated by attack (kept for backward compatibility)

#### Processing Phase Split (Enemy Turn Interruptibility)
The `"processing"` phase now uses `_processing_subphase`:
1. `"idle"` → Snapshot positions, move enemies, check AoO triggers. If triggers queued → enter `"awaiting_trigger"`, resume to `"post_movement"`.
2. `"post_movement"` → Resolve enemy attacks, end round, reset to `"player_input"`.

#### Main Loop Integration
- After `handle_events()`, the battle loop now checks for `awaiting_trigger` phase and routes modal clicks (`trigger_accept`/`trigger_decline`) to `resolve_current_trigger()`
- When all triggers are resolved, `turn_phase` returns to `_trigger_resume_phase`
- `render()` now passes `modal=trigger_modal` when in `awaiting_trigger` phase, using the existing `draw_modal_overlay()` system

### 🧪 Test Coverage
- **18 new tests** in `tests/test_combat_triggers.py`:
  - `TestTriggerQueue` (5 tests): queue/modal, accept callback, decline callback, empty modal, ordered resolution
  - `TestAttackOfOpportunity` (6 tests): AoO queued when leaving reach, no AoO staying in reach, no AoO when reaction used, accept uses reaction, reaction resets on turn, no AoO when enemy wasn't in reach
  - `TestWeaponMasteryTriggers` (4 tests): Push queues, Cleave queues with adjacent, Cleave skips without adjacent, Nick queues with offhand
  - `TestOnHitSpeciesTriggers` (2 tests): Goliath Fire queues, no trigger at 0 uses
  - `TestTriggerPhaseTransitions` (1 test): Push mastery hit enters awaiting_trigger phase
- **Total test count: 207 (189 existing + 18 new), all passing**

### 🔧 Architecture Impact
- **No breaking changes** — existing on-hit button system (pending_on_hit_actions) still exists but is inactive
- Weapon mastery apply methods (`_apply_push_mastery`, `_apply_cleave_mastery`, `_apply_nick_mastery`) unchanged — just called from trigger callbacks now
- Modal rendering reuses existing `draw_modal_overlay()` in gui.py — no GUI changes needed
- Sap, Slow, Topple, Vex, Graze masteries remain auto-applied (no player choice needed per SRD)

### 📌 Resume Notes
- The trigger system is extensible: any future reaction/decision can use `queue_trigger()` with a callback
- Deflect Attack (Monk reaction) and Shield spell (Wizard reaction) are natural candidates for future triggers
- `pending_on_hit_actions` and sidebar button approach are vestigial — can be removed in a cleanup pass
- The `extra_actions` / `extra_action_tooltips` render params still work but are no longer used for on-hit features
- Phase 3 seasonal loop remains the next major milestone

---

## 📋 Session 14 - Fog of War & Raid Direction System

### ✅ COMPLETED THIS SESSION

#### Fog of War / Vision System (main_gui.py + gui.py)
- **Player vision range:** Base 10 cells + Perception skill bonus + darkvision_range/5
  - Humans see ~11 cells, darkvision 60ft species see ~23, darkvision 120ft see ~35
- **`compute_player_visibility()`** — Chebyshev distance + Bresenham LOS raycasting
  - Rocks block LOS; trees do not (consistent with existing cover system)
  - Results cached in `_visible_cells`, recomputed on every move/teleport
  - Lazy recomputation: `is_cell_visible()` auto-recomputes if cache is stale
- **Rendering:** Semi-transparent dark overlay on non-visible cells; enemies in fog are fully hidden (no circle, name, or HP bar)
- **Targeting restrictions:** All targeting methods (`attack_enemy_at`, `cast_spell_at`, `cast_aoe_spell_at`, `breath_weapon_enemy_at`, `species_magic_enemy_at`, `apply_hunters_mark_at`) reject targets in fogged cells with "You can't see that area."
  - Exception: Self-centred AoE spells (e.g. Thunderwave, `burst_self` shape) bypass fog check

#### Raid Direction System (main_gui.py + gui.py)
- **Directional spawning:** `add_enemies()` picks 1-3 random sides (north/south/east/west), always leaving at least 1 side free for kiting
  - Rogues, Rangers, and mobile classes can flee toward the safe side
- **Edge spawning:** Enemies spawn within 3 cells of their assigned edge via `_spawn_position_for_side()`
- **Horn blast announcement:** `_generate_horn_blast_message()` generates thematic messages ("War horns sound from the North and East!")
  - Displayed as wave start message and logged to combat log
- **Raid direction indicators:** Red glow bars along raided map edges with directional labels (▼ N, ▲ S, ▶ W, ◀ E) rendered by `_draw_raid_direction_indicators()` in gui.py

#### New State Fields on GameState
- `raid_sides: list[str]` — Which sides enemies are raiding from (e.g. `['north', 'east']`)
- `_visible_cells: set[tuple[int, int]]` — Cached visible cell set
- `compute_player_visibility()` — Called on init, move, teleport (Cloud Jaunt), gate pass
- `is_cell_visible(x, y)` — Lazy accessor with stale-cache detection
- `_player_vision_range()` — Vision range calculation

#### New render() Parameters (gui.py)
- `fog_visible_cells: Optional[set]` — Passed from GameState._visible_cells
- `raid_sides: Optional[list[str]]` — Passed from GameState.raid_sides
- New colors: `COLOR_FOG = (0, 0, 0, 160)` and `COLOR_RAID_GLOW = (200, 40, 40)`

#### Tests — 20 new tests in tests/test_fog_of_war.py
- `TestPlayerVisionRange` (3 tests): base vision, darkvision extension, high darkvision
- `TestVisibilityComputation` (6 tests): player pos visible, adjacent cells, far cells hidden, rock LOS blocking, lazy recompute, movement updates
- `TestRaidDirectionSpawning` (4 tests): 1-3 sides, at least 1 free, correct edges, not in keep
- `TestHornBlastMessage` (3 tests): 1/2/3 side messages
- `TestFogOfWarTargeting` (4 tests): can't attack fogged enemies, can attack visible, can't cast at fogged, self-AoE ignores fog
- **Total test count: 175 (155 existing + 20 new), all passing**

### 🔧 Architecture Impact
- **No breaking changes** — fog_visible_cells and raid_sides are optional render() params (default None = no fog)
- Intermission screen deliberately does not pass fog data (full visibility during intermission)
- Existing stealth/hidden system unchanged — fog of war is complementary (player can't see enemies, stealth is enemies can't see player)

---

## 📋 Session 13 - SRD Level-1 Class Features + Combat Polish

### ✅ COMPLETED THIS SESSION

#### Combat Polish (Early Session)
- Fixed Pylance type errors in 4 test files
- Enhanced combat log with detailed dice roll breakdowns (d20 rolls, modifiers, totals)
- Fixed Goliath Fire Ancestry test (119/119 pass)
- Fixed enemy ranged-in-melee disadvantage detection
- Fixed Prone condition to SRD-compliant Advantage/Disadvantage system

#### Level-1 Class Features (4 New Features)

**Fighting Style (Fighter lv1)** — Character creator choice from 4 styles:
- **Archery:** +2 to ranged weapon attack rolls (hooked into `get_attack_bonus_total()`)
- **Defense:** +1 AC while wearing armor (hooked into `get_ac()`)
- **Great Weapon Fighting:** Reroll 1s and 2s on damage dice for Two-Handed/Versatile weapons (`_is_gwf_eligible()`, `_roll_gwf_dice()`, applied in `attack()` base/crit/Savage Attacker rolls)
- **Two-Weapon Fighting:** Available as selection (TWF mechanics pending dual-wield system)

**Expertise (Rogue lv1, Bard lv2)** — Choose 2 proficient skills for doubled proficiency:
- New `get_skill_bonus(skill_name)` method with full 18-skill SKILL_ABILITIES mapping
- Expertise doubles proficiency bonus on chosen skills
- Stealth bonus in `main_gui.py` now uses `get_skill_bonus("Stealth")`

**Innate Sorcery (Sorcerer lv1)** — Bonus action, 2 uses/LR, 10-round duration:
- +1 to spell save DC via `get_spell_save_dc()` while active
- Advantage on Sorcerer spell attack rolls in `cast_spell()` (rolls second d20, takes higher)
- Round countdown in `end_round()`, reset in `rest_features()`
- GUI button added in `gui.py` feature_map + action handler in `main_gui.py`

**Favored Enemy (Ranger lv1)** — Hunter's Mark always prepared + 2 free casts/LR:
- Hunter's Mark available at level 1 (was level 2)
- `use_hunters_mark()` checks `favored_enemy_free_casts` before feature uses
- Free casts reset on long rest in `rest_features()`

#### Character Creator Integration
- New **Fighting Style selection screen** for Fighters (4 options with descriptions)
- New **Expertise selection screen** for Rogues (pick 2 from proficient skills)
- `_advance_to_class_feature_screen()` routing helper (Fighter→style, Rogue→expertise, else→species)
- Both screens fully integrated: click handlers, hover effects, render, review display, preset saving

### 🧪 Test Coverage
- **22 new tests** in `tests/test_class_features_lv1.py`:
  - Fighting Style: Archery +2 ranged, no melee effect, Defense +1 with armor, no effect without, GWF eligibility (Two-Handed, Versatile, shield blocks), GWF reroll behavior
  - Expertise: doubled proficiency, normal proficiency, unproficient skill
  - Innate Sorcery: activation, double-activate blocked, +1 DC, DC only for Sorcerer, round countdown, rest reset
  - Favored Enemy: free casts init, non-Ranger zero, free-casts-first order, rest reset
- **Total:** 141 tests, all passing

### 📌 Resume Notes
- All 4 class features are gameplay-functional with character creator integration
- TWF fighting style is selectable but effects are pending dual-wield system implementation
- Remaining level-1 features: Divine Order (Cleric), Druidic + Primal Order (Druid), Eldritch Invocations (Warlock), Thieves' Cant (Rogue)
- Phase 3 seasonal loop remains the next major milestone

---

## 📋 Session 12 - Origin Feats Implementation + Cover Mechanics Fix

### ✅ COMPLETED THIS SESSION

#### Origin Feats (All 10 — Previously Non-Functional)
All 10 origin feats were stored as strings in `self.origin_feats` but had **zero gameplay effects**. Now fully implemented:

- **Alert:** +Proficiency Bonus to initiative rolls (`roll_initiative()`)
- **Magic Initiate (Cleric/Druid/Wizard):** Grants 2 cantrips + 1 level-1 spell from chosen class. Free once/long-rest cast of the level-1 spell before spending slots. Non-casters get a dedicated spell slot. Spell slot preserved on level-up. Spellcasting ability matches the MI class (WIS for Cleric/Druid, INT for Wizard).
- **Savage Attacker:** Roll damage twice, take the higher result. Once per turn, resets at `start_turn()`.
- **Skilled:** +3 additional skill proficiencies chosen during character creation (from full `ALL_SKILLS` list).
- **Crafty:** +3 tool proficiencies chosen during character creation (from `TOOL_PROFICIENCY_OPTIONS`). 20% gold discount on purchases (`get_buy_cost()`).
- **Healthy:** Reroll 1s on healing dice from spells and potions. Potions changed from flat heal (7) to rolling 2d4+2 (with reroll-1s for Healthy).
- **Iron Fist:** Reroll 1s on unarmed strike damage (Monk `martial_arts_strike()`).
- **Meaty:** +2 HP at character creation and +2 HP per level-up.

**Key implementation details:**
- New method `_initialize_origin_feats()` called from `__init__` after `_initialize_species_features()`
- New helper `has_origin_feat(keyword)` for substring matching (e.g., "Magic Initiate" matches all 3 variants)
- New helper `_get_mi_class()` extracts class from "Magic Initiate (Cleric)" etc.
- New helper `_roll_dice_reroll_ones()` for Healthy/Iron Fist reroll mechanic
- `character_creator_gui.py` updated: `_init_skill_select()` adds Skilled picks, `_init_tool_select()` adds Crafty picks
- Imports added to character.py: `CLASS_CANTRIP_OPTIONS`, `CLASS_LEVEL1_SPELL_OPTIONS` from spell_data

#### Cover Mechanics (4 SRD Violations Fixed)
Cover system in `main_gui.py` was non-compliant with SRD 5.2.1. All 4 issues resolved:

1. **No directionality** — Cover applied if ANY obstacle adjacent to target regardless of attacker position. Fixed: now uses Bresenham ray tracing from attacker to target + dot-product adjacency check. Only obstacles between attacker and target provide cover.
2. **Trees and rocks both +2 AC** — SRD defines two tiers. Fixed: trees = Half Cover (+2 AC), rocks = Three-Quarters Cover (+5 AC).
3. **Spells ignored cover** — Ranged spell attacks now check cover via `_cover_bonus(attacker_pos, target_pos)` in `cast_spell_at()`.
4. **Enemy ranged attacks ignored player cover** — `resolve_combat()` now applies cover bonus to player AC when enemies make ranged attacks.

**Method signature changed:** `_cover_bonus(target_pos)` → `_cover_bonus(attacker_pos, target_pos)`

### 🧪 Test Coverage
- **30 new tests** in `tests/test_origin_feats.py` covering all 10 feats
- **Total:** 119 tests (118 pass, 1 pre-existing Goliath Fire Ancestry fail)
- Pre-existing failure: `test_goliath_fire_ancestry_uses_are_pb_limited` (AssertionError: 2 != 0) — not addressed this session

### 📌 Resume Notes
- All origin feats are now gameplay-functional. Character creation properly grants feat-specific bonuses.
- Cover mechanics are SRD-aligned with directional ray tracing and two-tier AC bonuses.
- Potions now roll 2d4+2 instead of flat 7 HP (affects balance).
- Priority 0 seasonal-loop baseline remains the active development priority.
- Known issue: Goliath Fire Ancestry test still failing (pre-existing).

---

## 📋 Session 11 - Combat UX & Stealth/Visibility Polish

### ✅ COMPLETED THIS SESSION

- Refactored optional on-hit feature activation in `character.py` into a registry-driven system (same runtime behavior, easier extension path).
- Fixed player Rage usability in GUI flow by disabling auto-consume at combat start (`main_gui.py` now uses manual Rage activation).
- Improved combat panel action economy readability in `gui.py` with explicit status badges:
  - `A ✓ READY / ✗ USED`
  - `BA ✓ READY / ✗ USED`
- Added Temp HP visibility in UI player header (`HP current/max (+X THP)`), making Adrenaline Rush effects visible.
- Split character creator equipment flow into separate screens for legibility:
  - `weapon_select`
  - `armor_select`
  - Added Armor screen `Back` button while preserving selection/budget state.
- Reworked hide behavior from binary invisibility to contested stealth detection:
  - Hide now rolls Stealth vs enemy passive perception.
  - Detection requires enemy sight range and no obscuring terrain between enemy and player.
  - Enemies can reveal hidden players during resolution if checks pass.
- Ensured casting spells reveals player from hiding the same way attacks do.
- Added disadvantage messaging for ranged attacks made in melee:
  - combat log now includes `Disadvantage: Ranged in melee`.

### 🧪 Validation Completed

- Focused suites repeatedly passed during implementation:
  - `tests.test_main_gui_rewards`
  - `tests.test_main_gui_enemy_ai`
  - `tests.test_combat`
  - `tests.test_actions`
  - `tests.test_monster_speeds`
  - plus targeted on-hit/mastery tests from prior step continuation
- Diagnostics clean in edited files after each patch cycle.

### 📌 Resume Notes

- Current gameplay loop remains level-1 focused with XP banking and optional on-hit activations.
- Character creator now has separate weapon/armor selection screens with better detail-space.
- Stealth system now uses LOS/range/perception checks; spells and attacks both break hiding.
- Next best continuation remains Priority 0 seasonal-loop baseline and Phase 3 progression in `ROADMAP.md`.

---

## 📋 Session 10 - SRD Level-1 Feature Coverage Audit

### ✅ COMPLETED THIS SESSION

- Audited SRD level-1 class features from `SRD_CC_v5.2.1.md` against runtime implementation in `character.py`, `main_gui.py`, `gui.py`, and `spell_data.py`.
- Confirmed currently implemented in runtime flow: Rage, Unarmored Defense, Second Wind, Lay On Hands, Bardic Inspiration, Sneak Attack, baseline Spellcasting.
- Confirmed not yet implemented as gameplay mechanics (or only present as metadata text in `class_features.py`):
  - Fighting Style
  - Expertise (Rogue/Bard)
  - Weapon Mastery
  - Divine Order
  - Druidic
  - Primal Order
  - Martial Arts
  - Favored Enemy
  - Arcane Recovery
  - Innate Sorcery
  - Eldritch Invocations / full Pact interactions
  - Thieves’ Cant

### 📌 Follow-up Tracking

- Backlog was added to active TODOs and mirrored in `ROADMAP.md` under SRD level-1 parity work.
- Recommended implementation order for next return session:
  1. Fighter Fighting Style
  2. Rogue/Bard Expertise
  3. Weapon Mastery framework

---

## 📋 Session 9 - Phase 3 Slice 1 (Calendar + Keep Resource Loop)

### ✅ COMPLETED THIS SESSION

#### **Step 1: Keep Management Foundation Module**
- Added `keep_management.py` with `KeepState`:
  - Calendar tracking (`month`, `day`, month rollover)
  - Keep resources (`food`, `supplies`, `morale`)
  - Daily raid resolution method (`advance_raid_day`) with simple upkeep/effects

#### **Step 2: Runtime Integration in GUI Loop**
- Integrated persistent keep state into `main_gui.py`:
  - `KeepState` created once and preserved across waves
  - Wave outcomes now advance day and apply keep resource changes
  - Keep update messages are surfaced in run output after each wave

#### **Step 3: In-Combat UI Visibility**
- Added keep status line to bottom UI panel in `gui.py`:
  - Date (month/day)
  - Food
  - Supplies
  - Morale

#### **Step 4: Test Coverage**
- Added `tests/test_keep_management.py`:
  - Raid day resource updates
  - Month/day rollover validation

#### **Step 5: Validation**
- Targeted suite passed:
  - `tests.test_keep_management`
  - `tests.test_waves`
  - `tests.test_phase2_features`
- Compile checks passed for:
  - `keep_management.py`
  - `main_gui.py`
  - `gui.py`

### 📊 Current Project State

**Game Status:** Wave defense prototype with Phase 3 slice 1 live in runtime (v0.8.1)  
**Phase Status:** Phase 1 ✅ | Phase 2 ✅ | Phase 3 (Slice 1) ✅  
**Next Priority:** Complete Priority 0 seasonal-loop baseline (calendar + raid chaining + rest economy), then move to Phase 3 slice 2

---

## 🗂️ Archive Note

Older session entries were intentionally trimmed to keep this file focused and maintainable.
Full historical detail remains available in git history.
