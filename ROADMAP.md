# Development Roadmap & Decision Tree

**Current Version:** 0.2  
**Date:** 2026-02-08

This document helps you (or the next AI) decide what to work on next.

---

## ✅ What's Fully Complete

- [x] Terminal game (fully playable)
- [x] Interactive combat system
- [x] Character creation with 12 classes
- [x] Leveling system with XP progression
- [x] Loot and gold collection
- [x] Item drops (potions)
- [x] D&D 5.5e initiative system with tiebreakers
- [x] Attack rolls, critical hits, damage calculation
- [x] Color-coded UI (terminal)
- [x] Unit tests (15 tests, all passing)
- [x] Pygame GUI framework (needs Python 3.11)
- [x] Documentation (comprehensive)

---

## 🔧 What Needs Work

### High Priority (Easy to Medium)

**1. Test Pygame GUI on Python 3.11**
- Status: Framework complete, but unverified in actual play
- Time: 30 minutes
- Steps:
  1. Set up Python 3.11 environment
  2. Install pygame
  3. Run: `python main_gui.py --seed 42 --waves 1`
  4. Play a few waves, test click-to-move and combat
  5. Note any visual/gameplay issues
- Next: Report bugs and refine rendering

**2. Add Visual Sprites to GUI**
- Status: Characters are circles, keep is rectangle
- Time: 1-2 hours
- Approach:
  - Use simple shapes or emoji/Unicode symbols
  - Different colors for different enemy types
  - Keep it simple: no asset files needed yet
- Example:
  ```python
  if is_player:
      symbol = "🧙"  # Wizard
  elif enemy.behavior == "healer":
      symbol = "⚕️"   # Healer
  else:
      symbol = "👹"   # Regular enemy
  ```

**3. Add Ranged Combat**
- Status: All attacks are melee (adjacent only)
- Time: 2-3 hours
- Changes needed:
  - Add `range` property to Character
  - Modify attack logic to check distance
  - Some enemies attack from outside keep
- Example:
  ```python
  def can_attack(self, target, distance):
      return distance <= self.range
  ```

**4. More Enemy Variety**
- Status: Only basic Goblin/Archer/Champion
- Time: 1-2 hours
- Add to monsters.py:
  - Orc (melee, high damage)
  - Skeleton (ranged, low HP)
  - Troll (melee, regenerates)
  - Mage (ranged, casts spells)
- Make waves spawn different mixes

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
