# Development Roadmap & Decision Tree

**Current Version:** 0.8.6  
**Date:** 2026-02-22 (Updated: Session 16 — Staggered Enemy Turns + Enemy Stealth System)
**Status:** Core mechanics complete ✅ SRD-aligned ✅ Phase 1 complete ✅ Phase 2 complete ✅ Phase 3 Slice 1 live ✅ Origin Feats live ✅ Cover SRD-compliant ✅ Level-1 Class Features expanded ✅ Staggered combat ✅ Enemy stealth ✅

**📘 Long-Term Vision:** See [GAME_DESIGN.md](GAME_DESIGN.md) for comprehensive design guidance covering calendar system, keep management, NPCs, economy, and advanced features. Phase 3 has started in slices; roadmap tracks the next actionable implementation gates.

---

## 🔄 How to Resume Work

**When starting a new session:**

1. **Read Session 16 Summary in [CHANGELOG.md](CHANGELOG.md)** - Shows what was completed today
2. **Reference SRD Docs** - All rules now in local markdown files (8 reference docs)
3. **Check Current Priority** - Phase 3 implementation slices and milestone scoping (see below)
4. **Review [GAME_DESIGN.md](GAME_DESIGN.md)** - Long-term vision for context
5. **Run the game** to verify everything works:
   ```powershell
   py -3.11 main_gui.py
   ```

**Key Files to Know:**
- **CHANGELOG.md** - Complete session history and current state
- **ROADMAP.md** - This file, current priorities and next steps
- **GAME_DESIGN.md** - Long-term vision and design specifications
- **ARCHITECTURE.md** - Technical architecture and module guide
- **CLASS_REFERENCE.md** (and 7 other SRD docs) - Rules authority

**Current State Summary:**
- ✅ SRD 5.2.1 reference system established (8 local docs)
- ✅ All code aligned with SRD values (monsters, items, healing)
- ✅ Class features updated to match SRD
- ✅ All 10 origin feats gameplay-functional (30 tests)
- ✅ Cover mechanics SRD-compliant (directional, two-tier, spells + enemy ranged)
- ✅ Long-term design documented with phase gates
- ✅ Formula-based stats now used in all player creation paths
- 🎯 **Next:** Phase 3 slice progression - complete seasonal loop baseline, then event + keep upgrade path

---

## ✅ CRITICAL BLOCKER - RESOLVED

**Core Stat Calculations Now Formula-Based** ✅
- ✅ HP: Now calculated as (Hit Die // 2 + 1) + CON modifier
- ✅ AC: Now scales with armor type + DEX modifier
- ✅ Attack: Now calculated as ability mod + proficiency bonus
- ✅ Initiative: Now calculated as DEX modifier
- ✅ Damage: Now calculated as ability modifier

**What was done:**
1. ✅ Added ability score system (STR, DEX, CON, INT, WIS, CHA) to Character
2. ✅ Implemented `generate_level_1_stats()` function with verified 2024 D&D formulas
3. ✅ Created DEFAULT_ABILITY_SCORES for all 12 SRD classes
4. ✅ Updated character_creator_gui to use formula-based stats instead of CLASS_TEMPLATES

**Validation:**
- ✅ All 15 unit tests passing
- ✅ Ability modifiers correctly calculated: `(score - 10) // 2`
- ✅ Character creation generates stats from formulas, not hardcoded values
- ✅ Barbarian: STR 15 (+2), CON 14 (+2), HP = 9 (was 35, now formula-based)

**Files updated:**
- character.py - Added ability_scores, get_ability_modifier(), get_all_modifiers()
- class_definitions.py - Added generate_level_1_stats(), DEFAULT_ABILITY_SCORES
- character_creator_gui.py - Now uses generate_level_1_stats() instead of CLASS_TEMPLATES

---

## ✅ What's Fully Complete

- [x] Terminal game (fully playable)
- [x] Interactive combat system
- [x] Character creation (terminal + GUI)
- [x] Leveling system with XP progression
- [x] Loot and gold collection
- [x] Item drops (potions)
- [x] D&D 5.5e initiative system with tiebreakers
- [x] Attack rolls, critical hits, damage calculation
- [x] Color-coded UI (terminal)
- [x] Unit tests (15 tests, all passing)
- [x] Pygame GUI framework (Python 3.11)
- [x] Turn-based combat with pauses
- [x] GUI Character Creator (3-screen flow)
- [x] **Base Class Features (32 features across 12 SRD classes)**
- [x] **2024 D&D Class Definitions (verified sources)**
- [x] **Ability Score System (STR, DEX, CON, INT, WIS, CHA)**
- [x] **Formula-Based Stat Generation (HP, AC, Attack, Initiative)**
- [x] Python 3.11 environment setup
- [x] All linting errors fixed
- [x] Documentation (comprehensive)

---

## 🔧 NEXT PRIORITY TASKS

### Session 16 Closeout (2026-02-22)

**Completed this session (shipped):**
- ✅ Staggered enemy turns — enemies act one at a time with 1.5s pause between each
- ✅ Goblin Skulk sneaky archetype — spawns hidden, attacks with advantage + sneak attack dice, re-stealths behind cover
- ✅ Enemy stealth system — hidden_enemies tracking, active Perception rolls (d20+bonus), silent failure, AoE reveals
- ✅ 23 new stealth tests (`tests/test_enemy_stealth.py`), 230 total passing

**Carry-forward priority unchanged:** complete Priority 0 seasonal-loop baseline, then continue Phase 3 slices.

### Session 12 Closeout (2026-02-20)

**Completed this session (shipped):**
- ✅ All 10 origin feats implemented with gameplay effects (were completely non-functional)
- ✅ 30 new feat tests in `tests/test_origin_feats.py`
- ✅ Cover mechanics rewritten: directional Bresenham ray, trees +2 / rocks +5, spells + enemy ranged now check cover
- ✅ Potions now roll 2d4+2 instead of flat 7 HP
- ✅ Character creator updated for Skilled (+3 skills) and Crafty (+3 tools) feats

**Carry-forward priority unchanged:** complete Priority 0 seasonal-loop baseline, then continue Phase 3 slices.

### Session 11 Closeout (2026-02-19)

**Completed polish this session (shipped):**
- ✅ On-hit optional feature flow refactored to registry-based dispatch
- ✅ Rage activation fixed (manual bonus-action use, no auto-spend at combat start)
- ✅ Action/Bonus Action status readability improved with explicit READY/USED badges
- ✅ Temp HP display added to combat UI (`(+X THP)`)
- ✅ Character creator equipment split into separate Weapon and Armor screens (+ Armor Back button)
- ✅ Hide reworked to contested stealth vs passive perception with sight-range + obscuration checks
- ✅ Spell casting now reveals hidden player (same visibility break behavior as attacking)
- ✅ Ranged attacks in melee now surface disadvantage reason in combat text

**Carry-forward priority unchanged:** complete Priority 0 seasonal-loop baseline, then continue Phase 3 slices.

### Priority 0: Phase 3 Seasonal Loop Baseline (ACTIVE)

**Goal:** Implement the documented day/season loop before adding advanced event and keep systems.

**Implementation Checklist:**
- [ ] Add seasonal calendar core: 25-day seasons, order Spring → Summer → Winter → Fall, 100-day year
- [ ] Add year-end level-up trigger (or hook point) at day 100 rollover
- [ ] Generate raid schedule at season start:
  - Total raids = `10 × player_level`
  - Per-day cap = `2 × player_level`
  - Randomly distribute raids across days within cap
- [ ] Add end-day raid chaining:
  - If raids remain on current day, `End Day` starts next raid
  - Day advances only after all current-day raids are completed
- [ ] Add post-raid auto short rest and reward-screen flow
- [ ] Add day-end long rest payment logic for raided days:
  - 1 raid/day = 100 food
  - Each additional raid same day = +50 food
  - Emergency fallback spends gold at defined emergency conversion
- [ ] Add exhaustion penalty when neither food nor gold can satisfy required day-end rest cost
- [ ] Add game-over checks for death or max exhaustion

**Map/Resource Setup for Baseline:**
- [ ] Spawn one 10×10 farmland patch not within 5 tiles of keep or forest
- [ ] Add baseline food economy values: start 100 food, storage cap 500, production 50/day
- [ ] Place 1×2 staircase opposite gate that transitions to 6×6 root cellar map

**Suggested Validation:**
- [ ] Simulate one full season at level 1 and verify raid count/cap behavior
- [ ] Simulate a multi-raid day and verify `End Day` chaining behavior
- [ ] Simulate low-food scenarios to verify gold fallback and exhaustion path

---

### Priority 1A: SRD Level-1 Class Feature Parity (DOCUMENTED BACKLOG)

**Context:** An audit against `SRD_CC_v5.2.1.md` confirmed several level-1 class features are still metadata-only (`class_features.py`) and not yet operational gameplay mechanics.

**Confirmed implemented:**
- Rage
- Unarmored Defense
- Second Wind
- Lay On Hands
- Bardic Inspiration
- Sneak Attack
- Baseline Spellcasting
- Martial Arts (implemented Session ~10)
- Weapon Mastery (implemented Session ~10)
- Arcane Recovery (implemented Session ~10)
- **All 10 Origin Feats (implemented Session 12)**
- **Cover Mechanics — SRD-compliant (implemented Session 12)**

**Outstanding level-1 mechanics to implement:**
- [x] Fighting Style — Archery, Defense, GWF, TWF (Fighter; implemented Session 13)
- [x] Expertise — doubled proficiency on 2 skills (Rogue/Bard; implemented Session 13)
- [ ] Divine Order (Cleric)
- [ ] Druidic + Primal Order (Druid)
- [x] Favored Enemy — Hunter's Mark at lv1 + 2 free casts/LR (Ranger; implemented Session 13)
- [x] Innate Sorcery — +1 DC, Advantage on spell attacks (Sorcerer; implemented Session 13)
- [ ] Eldritch Invocations and full Pact Magic interactions (Warlock)
- [ ] Thieves' Cant (Rogue; low combat impact but track for completeness)

**Recommended implementation order for future sessions:**
1. Divine Order (Cleric)
2. Druidic + Primal Order (Druid)
3. Eldritch Invocations (Warlock)

---

### Priority 1: Integrate Features into Combat (NOW POSSIBLE)

**Step 5: Feature Integration** ← NEW BLOCKER
- Time: 3-4 hours
- What: Make class features actually affect combat
- How:
  - Rage: +damage based on STR mod, resistance to physical damage
  - Sneak Attack: +damage with finesse weapons in advantageous position
  - Bardic Inspiration: Grants bonus to ally's next roll
  - Unarmored Defense (Monk): AC calculation already works in formula!
  - Channel Divinity: Turns undead or heals
  - Action Surge: Additional action per turn (needs action economy system)
- Requires: Enhanced combat loop that checks for active features
- Impact: Combat becomes mechanically meaningful, class choices matter

**What this enables:**
- Combat demonstrates class differences (Barbarian vs Wizard)
- Features have tangible mechanical effects
- XP progression becomes more strategic
- Game becomes more D&D-like

### Priority 2: Visual Enhancements

**4. Add Visual Sprites to GUI** (1-2 hours)
- Color/shape different enemy types
- Add text labels under characters
- Different colors for different threat levels

**5. Integrate Class Features into Combat** (2-3 hours)
- Add UI buttons to use features
- Implement Rage: +2 damage, resistance
- Implement Sneak Attack: +1d6 damage
- Implement healing features
- Track usage and reset on rest

### Priority 3: Ranged Combat & Variety

**6. Add Ranged Combat** (2-3 hours)
- Add range property to Character
- Modify attack logic for distance-based targeting
- Have enemy AI use ranged attacks

**7. More Enemy Variety** (1-2 hours)
- Add Orc, Skeleton, Troll, Mage to monsters
- Mix enemy types in waves

---

## 📚 KEY FILES FOR NEXT SESSION

When resuming, read these in order:

1. **CHANGELOG.md** - Session 5 summary (Phase 1 completion)
2. **ROADMAP.md** - Current priorities and next steps
3. **ARCHITECTURE.md** - Combat loop structure
4. **class_features.py** - Features to integrate in Phase 2

---

## 📋 Quick Reference

**To run the game:**
```powershell
py -3.11 main_gui.py          # GUI with character creator
python main.py --interactive  # Terminal version
python -m unittest discover tests  # Run tests
```

**To check implementation:**
- class_definitions.py has all correct formulas
- D&D_AUDIT_REPORT.txt shows what's wrong
- CHANGELOG.md shows session progress

---

## How to Resume
1. Read CHANGELOG.md for Session 12 summary
2. Run tests to verify baseline behavior
3. Start Priority 0: Phase 3 seasonal loop baseline
4. Update ROADMAP/CHANGELOG before clearing chat

---

## 📌 Backlog (After Priority 0)

### Combat & Encounter Depth
- Integrate class features into combat actions and AI decisions
- Expand ranged combat behavior and mixed enemy wave composition
- Add status effects and equipment progression with clear UI feedback

### Systems & Quality of Life
- Save/load run state
- Leaderboard and run summary metrics
- Sound and animation polish

### Long-Term Scope
- Keep all Phase 3+ implementation details in [GAME_DESIGN.md](GAME_DESIGN.md)
- Promote only currently actionable items into this roadmap

**Current Priority:** Begin Phase 3 in controlled slices with playability gates. Each phase must remain fully playable and fun before moving to the next.

---

**Last Updated:** 2026-02-20  
**Next Review:** After first playable Priority 0 slice (season calendar + raid chaining) is stable
