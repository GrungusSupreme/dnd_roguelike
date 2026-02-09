# Development Roadmap & Decision Tree

**Current Version:** 0.3  
**Date:** 2026-02-08 (Session 2)

This document helps you (or the next AI) decide what to work on next.

---

## ✅ What's Fully Complete

- [x] Terminal game (fully playable)
- [x] Interactive combat system
- [x] Character creation (terminal + **GUI version confirmed working**)
- [x] Leveling system with XP progression
- [x] Loot and gold collection
- [x] Item drops (potions)
- [x] D&D 5.5e initiative system with tiebreakers
- [x] Attack rolls, critical hits, damage calculation
- [x] Color-coded UI (terminal)
- [x] Unit tests (15 tests, all passing)
- [x] **Pygame GUI framework - Tested and working on Python 3.11**
- [x] **Turn-based combat with pauses (readable gameplay)**
- [x] **GUI Character Creator (full 3-screen flow)**
- [x] Python 3.11 environment setup
- [x] All linting errors fixed
- [x] Documentation (comprehensive)

---

## 🔧 Next Priority Tasks

### High Priority (Polish & Playability)

**1. Add Visual Sprites to GUI** ⭐ (RECOMMENDED NEXT)
- Status: Characters are circles, keep is rectangle - looks bare
- Time: 1-2 hours
- Approach:
  - Use colored rectangles/shapes for different enemy types
  - Player = green circle, Enemies = red/different colors by type
  - Keep = outlined rectangle (already done)
  - Add text labels under characters (enemy names)
- Impact: Makes game feel more polished
- Example:
  ```python
  # In gui.py draw_character():
  if is_enemy and "goblin" in character.name.lower():
      pygame.draw.rect(screen, RED, char_rect)  # Goblin = rect
  elif is_enemy and "archer" in character.name.lower():
      pygame.draw.circle(screen, ORANGE, center)  # Archer = orange
  ```

**2. Add Ranged Combat**
- Status: All attacks are melee (adjacent only)
- Time: 2-3 hours
- Changes needed:
  - Add `range` property to Character (e.g., Archers = 3 cells)
  - Modify attack logic: `if distance <= self.range: can_attack()`
  - Update enemy AI to attack from distance
  - Test with ranged enemies in waves
- Impact: Significant gameplay variety

**3. More Enemy Variety**
- Status: Only Goblin/Archer/Champion
- Time: 1-2 hours  
- Add to monsters.py:
  - **Orc** - Melee, high damage (1d12+3), medium AC
  - **Skeleton** - Ranged, fragile (low HP), d20+2 attack
  - **Troll** - Melee, high HP, regenerates (heals 2 HP/turn)
  - **Mage** - Ranged spellcaster, low HP, can debuff
- Make waves mix enemy types
- Impact: Prevents boring predictable waves

---

## 📋 Medium Priority (Feature Expansion)

**4. Class-Specific Abilities** (Medium - 4-6 hours)
- Barbarian: Rage (double damage, -2 AC for 3 turns)
- Rogue: Sneak Attack (extra damage if at range, once per target)
- Cleric: Healing (heal self or ally for 2d4+WIS)
- Wizard: Fireball (AoE damage in 10ft radius)
- Paladin: Smite (add 2d6 to next attack)
- Bard: Inspire Ally (bonus attack for ally)

**5. Equipment System** (Medium - 4-5 hours)
- Drop better weapons/armor from loot
- Equipment affects AC, attack_bonus, damage
- UI to show equipped items
- Example: `Hero has Longsword (+1 dmg), Plate Armor (+2 AC)`

**6. Status Effects** (Medium - 3-4 hours)
- Poison (take damage each turn)
- Stun (skip next turn)
- Bleed (cumulative damage)
- Strength boost (+1 attack for N turns)
- Track active effects in Character

---

## 🌟 Low Priority (Polish & Scope)

- [ ] Save/load game state (pickle Character/GameState)
- [ ] Leaderboard (high scores with date)
- [ ] Sound effects (pygame.mixer)
- [ ] Animation (smooth character movement)
- [ ] Better grid visuals (hexagonal grid option)
- [ ] Map system (multiple keep areas)

---

## Quick Decision Matrix

**If you have 30 min:** Add sprite colors/shapes  
**If you have 1-2 hours:** Sprite polish + ranged combat baseline  
**If you have 3-4 hours:** Ranged combat + more enemy types  
**If you have 5+ hours:** Start on class abilities  

---

## How to Resume
1. Read CHANGELOG.md for Session 2 summary
2. Run: `py -3.11 main_gui.py` to verify everything works
3. Pick task from above (recommended: Visual Sprites first)
4. Update ROADMAP when tasks complete
5. Before clearing chat: Update CHANGELOG + ROADMAP + commit

### Medium Priority (Medium to Hard)

**5. Status Effects**
- Status: No poison, stun, bleeding, etc.
- Time: 3-4 hours
- Implementation:
  - Add `status_effects` dict to Character
  - Add effect types: poison (damage/round), stun (skip turn), etc.
  - Update attack logic to apply/check effects
  - Update UI to show active effects

**6. Equipment System**
- Status: No weapons or armor
- Time: 4-5 hours
- Items needed:
  - Weapon: `attack_bonus+1`, `dmg_bonus+2`, etc.
  - Armor: `ac_bonus+2`
  - Accessories: `hp+5`, `initiative+1`, etc.
- Implementation:
  - Add equipment slots to Character
  - Modify character creation to equip starting gear
  - Add loot tables (gear + potions)

**7. Class Abilities**
- Status: All classes play identically
- Time: 4-6 hours
- Examples per class:
  - Barbarian: Rage (2x damage, +temp HP)
  - Rogue: Sneak Attack (bonus damage)
  - Paladin: Smite (bonus damage vs evil)
  - Wizard: Fireball (damage all nearby)
- Implementation:
  - Add `abilities` list to Character
  - Each ability gets action slot
  - Abilities have cooldowns or resource costs

### Low Priority (Nice to Have)

**8. Save/Load System**
- Status: No persistence between sessions
- Time: 2-3 hours
- Approach: JSON serialization of game state
- Benefits: Continue long runs

**9. Leaderboard**
- Status: No tracking of best runs
- Time: 2-3 hours
- Track: waves survived, gold collected, kill count
- Storage: Local file (scores.json)

**10. Sound Effects**
- Status: Silent game
- Time: 3-4 hours (if using existing assets)
- Sounds: Attack hit, XP gain, level up, death

---

## 🎯 Suggested Paths Forward

### Path A: Polish GUI First
1. Test on Python 3.11
2. Add visual sprites/emoji
3. Improve UI panel (better formatting)
4. Then: Add ranged combat

**Outcome:** Beautiful, playable GUI version

### Path B: Deepen Gameplay
1. Add status effects
2. Add more enemy variety
3. Implement class abilities
4. Then: Equipment system

**Outcome:** More strategic, deeper combat

### Path C: Full Featured (Balanced)
1. Test GUI on 3.11
2. Add ranged combat
3. Add status effects
4. Add 5 new enemy types
5. Polish UI

**Outcome:** Complete, balanced game

### Path D: Quick Wins (Fastest)
1. More enemy variety (30 min)
2. Terminal UI improvements (1 hour)
3. Add one status effect (poison) (1 hour)

**Outcome:** More to do, but visible progress fast

---

## Decision Tree

```
What do you want to do?

├─ Make the GUI work
│  └─ "Need new features or just testing?"
│     ├─ "Just test" → See "Path A" step 1
│     └─ "Add features" → See "Path A"
│
├─ Make combat deeper
│  └─ "What appeals most?"
│     ├─ "Abilities per class" → Implement class abilities (7)
│     ├─ "More enemy types" → Add enemies (4)
│     └─ "Status effects" → Implement effects (5)
│
├─ Polish & fix bugs
│  └─ Run tests, check documentation, see ISSUES
│
└─ Long-term features
   └─ Equipment (6), Save/Load (8), Leaderboard (9)
```

---

## Quick Assessment

**Which task should I do first?**

**If this is Week 1:** Test GUI + add sprites (1-2 hours impact)

**If this is Week 2:** Ranged combat OR more enemies (bigger gameplay impact)

**If this is Week 3+:** Equipment + class abilities (depth multiplier)

**If you have 1 hour:** Add more enemy types to waves.py

**If you have 4 hours:** Implement one class ability (e.g., Barbarian Rage)

**If you have 8 hours:** Add status effects system

---

## How to Implement: Templates

### Template 1: New Enemy Type

```python
# In monsters.py
"Orc": {
    "hp": 20,
    "ac": 14,
    "attack_bonus": 6,
    "dmg_num": 1,
    "dmg_die": 10,
    "dmg_bonus": 4,
    "initiative_bonus": 0,
    "bounty": 5,
}
```

### Template 2: New Status Effect

```python
# In character.py
def apply_poison(self, rounds=3, damage_per_round=2):
    self.status_effects["poison"] = {
        "rounds": rounds,
        "damage": damage_per_round
    }

# In combat loop
def resolve_effects(self):
    if "poison" in self.status_effects:
        self.hp -= self.status_effects["poison"]["damage"]
        self.status_effects["poison"]["rounds"] -= 1
```

### Template 3: New Class Ability

```python
# In character.py
def use_ability(self, ability_name, target):
    if ability_name == "rage":
        self.dmg_bonus += 2
        self.temp_hp += 10
        self.ability_cooldowns["rage"] = 5  # 5 rounds
```

---

## Tips for Next Session

1. **Run tests first:** `python -m unittest discover`
2. **Make small changes:** One feature at a time
3. **Test afterward:** Run full test suite
4. **Document changes:** Update CHANGELOG.md
5. **Commit frequently:** Small, atomic commits

---

## Blocked By

❌ **Pygame on Python 3.14** - Wait for 3.11 environment

✅ **Everything else** - Unblocked, ready to go

---

## Quick Wins (Under 30 Minutes)

- [ ] Add Orc/Skeleton to monster types
- [ ] Add "spell" in Wizard class description
- [ ] Improve round summary formatting
- [ ] Add enemy count to UI panel
- [ ] Add level-up visual indicator

---

**Last Updated:** 2026-02-08  
**Next Review:** After trying Path A or B
