# dnd_roguelike — Changelog & Project State

**Last Updated:** 2026-02-14 (Session 9 - Phase 3 Slice 1)  
**Version:** 0.8.1 (Calendar + Keep Loop Foundation)

This file documents the complete project state for reference when clearing chat history.

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
**Next Priority:** Phase 3 slice 2 - add one random event type and one keep upgrade path

---

## 📋 Session 8 - Phase 2 Completion

### ✅ COMPLETED THIS SESSION

#### **Step 1: Character Sheet + Equipment UX Integration**
- Added dedicated character-sheet popup with D&D-style sections (abilities, skills, proficiencies, equipment, inventory, attunement slots).
- Added sheet actions and hotkeys (`C`/`I`) with modal behavior.
- Added clickable equipment management from sheet (equip/unequip main hand, offhand, armor).

#### **Step 2: Combat Visual Readability Upgrades**
- Added enemy archetype visual colors and threat ring indicators.
- Added on-map HP labels and panel legend for threat colors.

#### **Step 3: Enemy Variety Expansion (Phase 2 requirement)**
- Added multiple enemy archetypes in runtime waves:
  - Orc
  - Skeleton
  - Troll
  - Goblin Mage
- Updated wave composition to mixed-roster spawns by wave tier.
- Added distinct behaviors:
  - Troll regeneration each enemy phase
  - Healer support behavior for allied enemies
  - Mage poison application chance on hit

#### **Step 4: Remaining Feature Integration Gaps Closed**
- Implemented Action Surge as a true extra-action economy gain (not just a message).
- Added class-based Unarmored Defense formulas to AC:
  - Barbarian: `10 + DEX + CON`
  - Monk: `10 + DEX + WIS`
- Added lightweight status-effect system with combat impact (`Poisoned` attack penalty) and UI status display.

#### **Step 5: Test Coverage and Validation**
- Added `tests/test_phase2_features.py` for:
  - Unarmored Defense (Barbarian/Monk)
  - Poisoned attack penalty
  - Action economy gain for Action Surge
- Expanded wave tests for mixed archetype coverage and late-wave Troll/Mage presence.
- Focused Phase 2 validation suite passed:
  - `tests.test_phase2_features`
  - `tests.test_waves`
  - `tests.test_healer`
  - `tests.test_spells`
  - `tests.test_species_traits`

### 📊 Current Project State

**Game Status:** Wave defense prototype with Phase 2 feature integration completed (v0.8.0)  
**Phase Status:** Phase 1 ✅ | Phase 2 ✅ | Phase 3 planning next  
**Next Priority:** Begin first constrained Phase 3 vertical slice

---

## 📋 Session 7 - Spellcasting + Species Trait Completion

### ✅ COMPLETED THIS SESSION

#### **Step 1: Combat Spellcasting Framework**
- Added centralized spell metadata and slot tables in `spell_data.py`.
- Added level-1 caster spell selection requirements and options by class.
- Added runtime spell slot tracking, slot display, and spell casting APIs in `character.py`.
- Added spell actions to GUI with submenu behavior to reduce action bar clutter.

#### **Step 2: Spell Combat Effects + AoE Preview**
- Implemented combat effects for cantrips and level-1 combat spells.
- Added AoE spell casting path and per-spell AoE shape metadata support.
- Added live cursor-based AoE preview in GUI with valid/invalid coloring.
- Fixed spell attack resolution to use spellcasting modifier + proficiency.

#### **Step 3: Species Trait Mechanics Expansion**
- Expanded species passives and actives in `character.py`:
  - Dragonborn resistance + Breath Weapon usage scaling.
  - Tiefling fire resistance and lineage magic support.
  - Gnome mental save advantage support (Gnomish Cunning).
  - Halfling Lucky d20 reroll behavior.
  - Orc Relentless Endurance + Adrenaline Rush resource.
  - Goliath ancestry resource tracking and large-form activation hooks.
  - Dwarf resilience/toughness/stonecunning resource scaffolding.
- Added species bonus-action UI actions in combat (`gui.py`/`main_gui.py`).

#### **Step 4: Character Creation + Preset Integration**
- Added spell selection flow to character creation for spellcasters.
- Persisted selected spells/slots to presets and restored them on load.
- Added species bonus-selection UI scaffolding for Human/Elf bonus choices.

#### **Step 5: Test Coverage**
- Added `tests/test_spells.py` and expanded `tests/test_species_traits.py`.
- Added checks for slot usage, healing/cantrip behavior, Fire Bolt regression, AoE casting, and key species mechanics.

### 📊 Current Project State

**Game Status:** Wave defense prototype (v0.6.0) with combat spellcasting and expanded species trait handling  
**Spellcasting:** Character creation + combat casting + slot tracking integrated  
**Species Traits:** Core combat-relevant traits broadly implemented with automated tests  

---

## 📋 Session 6 - Background ASI & Combat Improvements

### ✅ COMPLETED THIS SESSION

#### **Step 1: Fixed Level 1 HP Calculation (SRD-Compliant)**
- **class_definitions.py UPDATED**
  - HP formula corrected: `hit_die + CON modifier` (was using leveling-up formula)
  - Now matches SRD 2024 exactly:
    - Barbarian: 12 + Con, Fighter/Paladin/Ranger: 10 + Con
    - Bard/Cleric/Druid/Monk/Rogue/Warlock: 8 + Con
    - Sorcerer/Wizard: 6 + Con
  - All tests still pass ✅

#### **Step 2: Background Ability Score Increases (D&D 2024)**
- **character_creation_data.py UPDATED**
  - Added `BACKGROUND_ABILITY_SCORES` mapping all 16 backgrounds to 3 suggested abilities
  - Used paraphrased PHB 2024 data for ability score suggestions
- **character_creator_gui.py UPDATED**
  - New screen: "Background ASI" between background and species selection
  - Players choose: **+2/+1 split** OR **+1/+1/+1 to all three** suggested abilities
  - Interactive button selection with visual feedback
  - Applied after point buy, capped at 20
- **Flow:** Class → Name → Point Buy → Background → **Background ASI** → Species → Skills → Feat → Review

#### **Step 3: Removed Non-SRD Backgrounds**
- **Removed Folk Hero and Urchin** (2014 PHB only, not in 2024 SRD)
- Final count: **16 backgrounds** (Acolyte, Artisan, Charlatan, Criminal, Entertainer, Farmer, Guard, Guide, Hermit, Merchant, Noble, Sage, Sailor, Scribe, Soldier, Wayfarer)
- Cleaned from: `character_creation_data.py`, `GAME_DESIGN.md`

#### **Step 4: Two-Tier Obstacle System**
- **main_gui.py & gui.py UPDATED**
  - **Trees (70%):** Provide cover but DON'T block movement or line of sight
    - Color: Dark green `(40, 90, 40)`
    - Enemies can path through for better navigation
  - **Rocks (30%):** Provide cover AND block movement + line of sight
    - Color: Gray `(80, 80, 70)`
    - Enemies path around these
  - Both provide +2 AC cover bonus when adjacent
  - Cover spans entire 64×64 map with 6-block gap around keep (up from 2-block)
- **Result:** Dramatically improved enemy pathfinding while maintaining tactical cover

### 📊 Current Project State

**Game Status:** Wave defense prototype (v0.5.3) with full D&D 2024 character creation
**Phase 1:** Complete ✅ (formula-based stats + background ASI integrated)
**Combat System:** Functional with cover mechanics and improved obstacle pathfinding
**All 15 Tests:** Passing ✅

---

## 📋 Session 5 - Phase 1 Completion

### ✅ COMPLETED THIS SESSION

#### **Step 1: Formula-Based Defaults Everywhere**
- **creator.py UPDATED**
  - Terminal character creation now uses `generate_level_1_stats()` and ability scores
  - Point-buy feeds directly into formula-based stat generation
- **main.py UPDATED**
  - Default player now uses `generate_level_1_stats()`
  - Potion use/drop now uses SRD-aligned defaults (`create_potion_of_healing()`)
- **main_gui.py UPDATED**
  - Quick-start hero now uses `generate_level_1_stats()`
- **character_creator_gui.py UPDATED**
  - GUI creator fallback hero now uses `generate_level_1_stats()`

#### **Step 2: Phase 1 Validation**
- ✅ All 15 unit tests passing
- ✅ No remaining hardcoded player presets in default flows
- ✅ Terminal + GUI creation paths both formula-based

### 📊 Current Project State

**Game Status:** Wave defense prototype (v0.5) with SRD-aligned, formula-based stats
**Phase 1:** Complete ✅ (formula-based stats integrated across all creation paths)
**Next Priority:** Phase 2 - Feature Integration (class features in combat)

---

## 📋 Session 4 - SRD Reference System & Long-Term Design Vision

### ✅ COMPLETED THIS SESSION

#### **Step 1: SRD 5.2.1 PDF Conversion**
- **Converted SRD_CC_v5.2.1.pdf to Markdown**
  - Used pdfplumber library for text extraction
  - Split 343-page PDF into 8 organized reference documents:
    - RULES_REFERENCE.md (core mechanics, combat, conditions)
    - CLASS_REFERENCE.md (all 13 classes with features)
    - SPECIES_REFERENCE.md (playable species/races)
    - FEATS_REFERENCE.md (all feats and origin feats)
    - EQUIPMENT_REFERENCE.md (weapons, armor, adventuring gear)
    - SPELLS_REFERENCE.md (complete spell list)
    - MAGIC_ITEMS_REFERENCE.md (magic item catalog)
    - MONSTERS_REFERENCE.md (creature stat blocks)
  - All docs properly attributed with CC BY 4.0 license
  - Deleted original PDF (redundant after extraction)

#### **Step 2: Removed External References**
- **Eliminated all wikidot URLs** from codebase
- **Deleted D&D_2024_REFERENCE.md** (obsolete external links)
- **Updated all documentation** to reference local SRD docs only
- **Files modified:**
  - class_definitions.py (removed source_url field)
  - DOCUMENTATION_STANDARDS.md (mandate SRD-only usage)
  - README.md (updated reference section)
  - ARCHITECTURE.md (SRD references)
  - D&D_AUDIT_REPORT.txt (SRD references)

#### **Step 3: Code Alignment with SRD Values**
- **monsters.py UPDATED**
  - Goblin variants now match official SRD stat blocks:
    - Goblin Minion: AC 12, HP 7 (was generic scaling)
    - Goblin Warrior: AC 15, HP 10 
    - Goblin Boss: AC 17, HP 21
  - Added proper SRD attributes (STR 8, DEX 14, CON 10, etc.)
  
- **items.py UPDATED**
  - Added `create_potion_of_healing()` function
  - SRD values: 2d4+2 HP (7 average), 50 GP cost
  
- **character.py UPDATED**
  - `use_potion()` now defaults to amount=7 (SRD average)
  - `heal_ally()` now defaults to amount=7 (SRD average)

#### **Step 4: Class Features Aligned with SRD**
- **class_features.py UPDATED** (9 features corrected)
  - Barbarian Rage: Added full SRD details (B/P/S resistance, +2 damage, Advantage on STR, 10 rounds)
  - Barbarian Unarmored Defense: Added AC formula (10 + DEX + CON, shield allowed)
  - Bard Bardic Inspiration: Fixed to Bonus Action, CHA mod uses, 1-hour duration
  - Cleric Channel Divinity: Clarified multiple effects (Turn Undead, healing, etc.)
  - Cleric: Replaced incorrect "Healing Light" with correct "Divine Order" feature
  - Fighter Second Wind: Corrected max_uses to 2 (1 on Short Rest, all on Long Rest)
  - Rogue Sneak Attack: Updated recharge to "unlimited", clarified conditions
  - Rogue Expertise: Standardized description (4 skills at level 9)
  - Wizard Arcane Recovery: Clarified as Short Rest feature with proper formula

#### **Step 5: Cleaned Up Redundant Documentation**
- **Deleted 5 redundant files:**
  - output.md (raw PDF extraction)
  - pdf_to_md.py (conversion script, no longer needed)
  - IMPLEMENTATION_SUMMARY.md (outdated summary)
  - QUICKSTART.md (redundant with README)
  - GUI_NOTES.md (merged into other docs)

#### **Step 6: Long-Term Design Documentation**
- **Created GAME_DESIGN.md** (600+ lines)
  - Complete vision for kingdom management roguelike
  - 9 development phases (current: Phase 2)
  - Systems designed:
    - Calendar & time management (months, days, raids)
    - Keep building and territory management
    - Resource economy (gold, scrap tiers, food, production)
    - NPC recruitment and management
    - Random event system with skill checks
    - Advanced enemy AI and siege mechanics
  - **Mandatory between-phase playtesting checklist**
  - All design concerns addressed with resolutions

- **Design Decisions Finalized:**
  - ✅ Standard 5e grid system (not grid line movement)
  - ✅ Siege escalation with specific turn counts (warning Round 7, siege Round 10)
  - ✅ Monthly food budget (not daily tracking)
  - ✅ Backgrounds balanced at 15-20% bonuses
  - ✅ 30 foundation events for Phase 4
  - ✅ Lenient exhaustion thresholds (4-5 raid days)
  - ✅ Strict phase discipline with playtesting gates

- **Updated ROADMAP.md**
  - Added reference to GAME_DESIGN.md
  - Emphasized Phase 2 focus before long-term features
  - Added long-term vision summary

- **Updated ARCHITECTURE.md**
  - Added future architectural considerations
  - Documented grid system decision
  - Listed required modules for future phases

### 📊 Current Project State

**Game Status:** Wave defense prototype (v0.5) with SRD-aligned features  
**Code Alignment:** All monster/item/healing stats match SRD 5.2.1  
**Reference System:** 8 local SRD docs, all external refs removed  
**Documentation:** Complete design vision with phased roadmap  
**Next Priority:** Phase 2 - Feature Integration (class features in combat)

**Files Added This Session:**
- RULES_REFERENCE.md
- CLASS_REFERENCE.md
- SPECIES_REFERENCE.md
- FEATS_REFERENCE.md
- EQUIPMENT_REFERENCE.md
- SPELLS_REFERENCE.md
- MAGIC_ITEMS_REFERENCE.md
- MONSTERS_REFERENCE.md
- GAME_DESIGN.md

**Files Modified This Session:**
- monsters.py (SRD goblin stat blocks)
- items.py (SRD potion values)
- character.py (SRD healing defaults)
- class_features.py (9 features aligned with SRD)
- class_definitions.py (removed wikidot references)
- ROADMAP.md (long-term vision link)
- ARCHITECTURE.md (future systems, grid decision)
- DOCUMENTATION_STANDARDS.md (SRD mandate)
- README.md (updated references)
- D&D_AUDIT_REPORT.txt (SRD references)
- CHANGELOG.md (this file)

**Files Deleted This Session:**
- SRD_CC_v5.2.1.pdf
- output.md
- pdf_to_md.py
- D&D_2024_REFERENCE.md
- IMPLEMENTATION_SUMMARY.md
- QUICKSTART.md
- GUI_NOTES.md

---

## 📋 Session 3 (Extended) - Ability Score System & Formula-Based Stats

### ✅ COMPLETED THIS SESSION (STEPS 1-4 OF CORE MECHANICS FIX)

#### **Step 1: Ability Score System to Character**
- **character.py ENHANCED**
  - Added `ability_scores` parameter: `{"STR": 15, "DEX": 12, ...}`
  - New method: `get_ability_modifier(ability: str) -> int` 
    - Formula: `(score - 10) // 2` (proper 2024 D&D)
  - New method: `get_all_modifiers() -> dict` 
    - Returns all 6 ability modifiers at once
  - Ability scores are now first-class in Character model

#### **Step 2: Calculate Modifiers From Ability Scores**
- **class_definitions.py ENHANCED**
  - New function: `get_ability_modifier(ability_score: int) -> int`
  - Calculates modifier using proper D&D formula
  - Used throughout stat generation pipeline

#### **Step 3: Formula-Based Stat Generation (CRITICAL)**
- **class_definitions.py NEW FUNCTION: `generate_level_1_stats()`**
  - Generates level 1 stats directly from class + ability scores
  - **HP Formula:** `(hit_die // 2 + 1) + CON modifier` ✅ 2024 D&D compliant
  - **AC Formula:** Scales with armor type + DEX modifier bonus
    - Heavy: 16 (plain)
    - Medium: 12 + min(DEX, +2)
    - Light: 11 + DEX
    - Unarmored (Monk): 10 + DEX + WIS
  - **Attack Bonus:** `STR/DEX modifier + proficiency bonus (+2 at level 1)` ✅
  - **Damage Bonus:** `STR modifier` ✅
  - **Initiative:** `DEX modifier` ✅
  - Returns dict: `{hp, ac, attack_bonus, dmg_num, dmg_die, dmg_bonus, initiative_bonus, ability_scores}`

- **DEFAULT_ABILITY_SCORES (NEW)**
  - Standard array [15, 14, 13, 12, 10, 8] distributed per class
  - Barbarian: STR 15, CON 14, WIS 13, DEX 12, INT 10, CHA 8
  - Wizard: INT 15, DEX 14, CON 13, WIS 12, CHA 10, STR 8
  - Monk: DEX 15, WIS 14, CON 13, STR 12, INT 10, CHA 8
  - (All 13 classes configured)

#### **Step 4: Sync CLASS_TEMPLATES with CLASS_DEFINITIONS**
- **character_creator_gui.py REFACTORED**
  - Changed from hardcoded `CLASS_TEMPLATES` lookup to `generate_level_1_stats()`
  - Import added: `from class_definitions import generate_level_1_stats`
  - `draw_review()` now shows:
    - Ability scores (STR, DEX, etc.) with modifiers
    - Calculated HP, AC, Attack, Damage, Initiative
  - `_create_character()` passes `ability_scores` to Character.__init__()
  - Deprecation: `CLASS_TEMPLATES` still exists but unused (kept for legacy)

### 📊 VALIDATION & TEST RESULTS

**All 15 unit tests passing** ✅
- test_combat (6 tests)
- test_leveling (2 tests)
- test_loot (2 tests)
- test_items (1 test)
- test_waves (3 tests)
- test_healer (2 tests)
- test_actions (2 tests)

**Character Creation Test Results:**
```
Barbarian:  STR 15 (+2), CON 14 (+2), DEX 12 (+1)
  HP: 9 | AC: 13 | Attack: +4 | Damage: +2 | Initiative: +1
  
Fighter:    STR 15 (+2), CON 14 (+2), DEX 12 (+1)
  HP: 8 | AC: 16 | Attack: +4 | Damage: +2 | Initiative: +1
  
Wizard:     INT 15 (+2), CON 13 (+1), DEX 14 (+2)
  HP: 5 | AC: 12 | Attack: +1 | Damage: -1 | Initiative: +2
  
Cleric:     WIS 15 (+2), CON 14 (+2), STR 13 (+1)
  HP: 7 | AC: 13 | Attack: +3 | Damage: +1 | Initiative: +1
```

### 🔄 CRITICAL BLOCKER STATUS

**Was:** "Core Stat Calculations Not Formula-Based (CRITICAL BLOCKER)"
**Now:** **RESOLVED** ✅

Stat generation now follows 2024 D&D rules with traceable formulas:
- ✅ HP derived from hit die + CON mod (not hardcoded)
- ✅ AC scales with armor/DEX (not constant)
- ✅ Attack/Damage based on ability modifiers
- ✅ Initiative based on DEX (not initiative_bonus override)

### 🎯 READY FOR STEP 5

Integration capability unlocked. Features like Rage can now:
- Check STR modifier for damage scaling
- Check CON modifier for HP calculations
- Use AC formula when calculating armor benefits
- Properly adjust initiative based on DEX

## 📋 Session 3 - EARLIER WORK (Class Features & Audit)

### ✅ COMPLETED EARLIER THIS SESSION

### ✅ COMPLETED THIS SESSION

#### Part 1: Base Class Features System
- **class_features.py** - Complete 2024 D&D-compliant feature system
  - 13 classes with 1-4 features each (32 total features)
  - ClassFeature class with usage tracking and recharge mechanics
  - Features: Rage, Sneak Attack, Bardic Inspiration, Channel Divinity, etc.
  - Support for "rest", "combat", "unlimited" recharge types
  - Methods: `use()`, `restore()`, status tracking

- **character.py UPDATED**
  - Added `class_name` parameter to Character.__init__()
  - Added `features` list loaded from class_features
  - New methods: `use_feature()`, `get_feature()`, `get_available_features()`, `rest_features()`, `display_features()`

- **character_creator_gui.py UPDATED**
  - Shows class features in review screen
  - Added import: `from class_features import get_class_feature_summaries`
  - Passes `class_name` when creating Character

#### Part 2: Critical 2024 D&D Rules Audit
- **IDENTIFIED CRITICAL ISSUE**: Core stats are hardcoded, not formula-based
  - HP values: hardcoded (Barbarian 35, should be 14 = d12 + CON+2)
  - AC values: hardcoded, no armor/DEX connection
  - Attack Bonus: hardcoded, should be ability mod + proficiency
  - Initiative: hardcoded, should be DEX modifier only
  - Damage Bonus: hardcoded, should be ability modifier

- **class_definitions.py** - VERIFIED 2024 D&D source data
  - All 13 classes with hit dies from SRD 5.2.1 reference docs
  - Source URLs for verification
  - ClassDefinition with calculation methods (properly formula-based)
  - Example: `calculate_hp(level, con_mod)` uses d12 + con_mod
  - Proficiency bonus table correct (2024 D&D)

- **D&D_AUDIT_REPORT.txt** - Detailed findings document
  - Shows all discrepancies with examples
  - Links to official 2024 D&D sources
  - Recommends integration path forward

- **DND_RULES_VERIFICATION.txt** - Problem documentation
  - Lists what should be fixed
  - Specifies 2024 D&D formulas for each stat

### ✅ TEST STATUS
- **15/15 Unit Tests**: PASSING ✓
- **Syntax Check**: All files compile ✓
- **Feature System**: Verified working (passive + limited features) ✓

### 📊 FILES MODIFIED/CREATED

**Modified:**
- character.py (added class_name, features list, feature methods)
- character_creator_gui.py (added feature display, class_name parameter)
- CHANGELOG.md (this file)
- ROADMAP.md (updated priorities)

**Created:**
- class_features.py (32 features for 13 classes)
- class_definitions.py (verified 2024 D&D class data)
- D&D_AUDIT_REPORT.txt (audit findings)
- DND_RULES_VERIFICATION.txt (problem details)

### ⚠️ CRITICAL NEXT STEPS (HIGH PRIORITY)

1. **Implement Ability Score System** (BLOCKING - core foundation)
   - Add STR, DEX, CON, INT, WIS, CHA to Character class
   - Use standard array [15, 14, 13, 12, 10, 8] or point buy
   - Calculate modifiers: (score - 10) // 2

2. **Replace Hardcoded Stats with Formula-Based Calculations**
   - HP = Hit Die + CON modifier per level
   - AC = Armor type + DEX modifier (varies by armor)
   - Attack Bonus = ability mod + proficiency bonus
   - Initiative = DEX modifier
   - Damage Bonus = ability modifier (STR/DEX per weapon)

3. **Integrate class_definitions.py** 
   - Use ClassDefinition.calculate_hp() for proper formula
   - Use ClassDefinition.get_proficiency_bonus() for level-based bonus
   - Reference source URLs in code comments

4. **Update Character Creator GUI**
   - Show ability score selection
   - Display calculated stats (not hardcoded values)
   - Show armor selection for AC calculation

### 📚 DOCUMENTATION COMPLETE
All findings documented in traceable files:
- class_definitions.py has all verified sources with links
- D&D_AUDIT_REPORT.txt shows discrepancies
- ROADMAP.md updated with integration tasks
- Each file has purpose-specific documentation

---

## 📊 COMPLETE PROJECT STATE

### ✅ FULLY WORKING
- Terminal game (main.py) - playable, all mechanics
- Pygame GUI (main_gui.py) - 64×64 grid, combat, character creator
- Character creation (interactive and GUI)
- Combat system (D&D 5.5e initiative, attacks, crits, healing)
- Leveling/XP progression
- Loot/gold system
- Item drops (potions)
- Class features (32 defined across 13 classes)
- 15 unit tests (all passing)

### ⚠️ NEEDS FIXING (HIGH PRIORITY)
- **Core stat formulas** - currently hardcoded, blocking realistic gameplay
- **Ability scores** - not in character system yet
- **AC calculation** - not armor-dependent
- **HP scaling** - doesn't use CON modifier
- **Attack/Damage** - not ability-score based

### 🎮 HOW TO RUN
```powershell
# GUI with character creator
py -3.11 main_gui.py

# Terminal version
python main.py --interactive

# Run tests
python -m unittest discover tests
```

### 📝 KEY REFERENCE FILES
- **class_definitions.py** - Verified 2024 D&D class data (use this for formulas)
- **class_features.py** - All 13 classes' features
- **character.py** - Character class (needs ability scores added)
- **D&D_AUDIT_REPORT.txt** - What needs to be fixed and why
- **ROADMAP.md** - Next task priorities

---

## NEXT SESSION CHECKLIST

When resuming work:

1. ✅ Read **D&D_AUDIT_REPORT.txt** - understand what needs fixing
2. ✅ Review **class_definitions.py** - see verified 2024 D&D formulas
3. ✅ Start with **ability score system** in character.py
4. ✅ Update Character.__init__() to use formulas instead of hardcoded values
5. ✅ Test with unit tests
6. ✅ Update GUI to show ability scores and calculated stats
7. ✅ Reference SRD 5.2.1 docs in this repo for any questions

All groundwork is complete - ready for implementation phase!

---

## SESSION 2 SUMMARY (2026-02-08)

### ✅ Completed
- Turn-based GUI gameplay with pauses
- Full 3-screen GUI character creator
- Python 3.11 environment setup
- Linting fixed (0 errors)
- Pygame validated

---

## SESSION 1

Initial project setup and core mechanics implementation.

- Pygame requires Python 3.11 (3.14 has distutils)
- GUI characters shown as circles, no sprite graphics yet
- Enemy AI basic (straight pathfinding)

## 🎮 Game Overview

**Genre:** Tactical roguelike wave-survival with D&D 5.5e combat

**Two Play Modes:**
1. **Terminal** (main.py) - Text-based, full interactivity, colorized
2. **Pygame GUI** (main_gui.py) - Visual grid, turn-based, character creator

**Core Loop:**
- Choose/create character
- Enemies spawn in waves 
- Player fights to win XP, gold, loot
- Level up to gain stats
- Survive N waves to win

## Project snapshot (2026-02-08, Session 2)
- Language: Python 3.14 (tests/terminal) + Python 3.11 (Pygame)
- Tests: `unittest` (15 tests, 100% passing)
- GUI Framework: Fully functional and tested
- Files: 14 Python files + 5 .md docs (ARCHITECTURE, ROADMAP, QUICKSTART, README, GUI_NOTES)

## Key modules
- `main.py`: interactive terminal combat with colors
- `main_gui.py`: pygame main loop, turn-based gameplay
- `gui.py`: pygame rendering (grid, keep, characters, UI panel)
- `character_creator_gui.py`: pygame GUI character creator (12 classes)
- `character.py`: Character model with D&D mechanics
- `waves.py`: Enemy spawning with wave scaling
- `creator.py`: Terminal character creator (fallback)
- `colors.py`: ANSI color codes for terminal UI
- Support: `dice.py`, `monsters.py`, `items.py`
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
