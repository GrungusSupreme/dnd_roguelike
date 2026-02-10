# D&D 2024 Reference Documentation

This document serves as a reference guide for D&D 2024 rules, mechanics, and content related to the Roguelike game implementation.

**Wiki Base:** http://dnd2024.wikidot.com/

---

## Table of Contents

1. [Bastions (Base Building System)](#bastions)
2. [Character Classes](#character-classes)
3. [Spellcasting](#spellcasting)
4. [Species & Subclasses](#species--subclasses)
5. [Combat & Rules](#combat--rules)

---

## Bastions

**Reference:** http://dnd2024.wikidot.com/bastions

The Bastion system provides mechanics for crafting, fortifying, and managing a keep as player characters level up. Key features include:

### Bastion Progression
- **Level 5:** 2 Special Facilities (chosen from available options)
- **Level 9:** +2 Special Facilities (4 total)
- **Level 13:** +1 Special Facility (5 total)
- **Level 17:** +1 Special Facility (6 total)

### Basic Facilities
Starting facilities at level 5 (choose 2):
- Bedroom
- Dining Room
- Parlor
- Courtyard
- Kitchen
- Storage

### Special Facilities by Tier

**Level 5 Facilities:**
- Smithy (Craft)
- Armory (Empower)
- Barrack (Recruit)

**Level 9 Facilities:**
- Arcane Study (Craft)
- Archive (Research)
- Garden (Harvest)
- Greenhouse (Harvest)
- Guildhall (Recruit)
- Laboratory (Craft)
- Library (Research)
- Observatory (Empower)
- Pub (Research)
- Reliquary (Harvest)
- Sacristy (Craft)
- Scriptorium (Craft)
- Stable (Trade)
- Storehouse (Trade)
- Teleportation Circle (Recruit)
- Theater (Empower)
- Training Area (Empower)
- Trophy Room (Research)
- War Room (Recruit) - Special: Requires Fighting Style or Unarmored Defense

**Level 13 Facilities:**
- Meditation Chamber (Empower)
- Menagerie (Recruit)

**Level 17 Facilities:**
- Demiplane (Empower)
- Sanctum (Empower)

### Hireling Orders
Actions issued to facilities each turn:
- **Craft:** Create items/equipment
- **Empower:** Enhance abilities or train
- **Harvest:** Gather resources
- **Maintain:** Upkeep the Bastion
- **Recruit:** Add defenders or creatures
- **Research:** Gather information
- **Trade:** Buy/sell goods

### Eberron-Specific Facilities
- Construct Forge (Level 17)
- Manifest Zone (Level 13)
- Various faction-specific facilities

---

## Character Classes

### Class Overview & Progression

All classes advance from level 1 to 20 with distinct feature progression. Each class gains ability score improvements at regular intervals.

### Core Classes

#### Artificer
**Reference:** http://dnd2024.wikidot.com/artificer:main
- **Primary Ability:** Intelligence
- **Hit Die:** d8
- **Key Features:**
  - Spellcasting (Prepared spells from Artificer list)
  - Tinker's Magic (INT modifier uses, regain on Long Rest)
  - Replicate Magic Item (Level 2+)
  - Magic Item Tinker (Level 6)
  - Flash of Genius (Level 7)
  - Subclasses: Alchemist, Armorer, Artillerist, Battle Smith, Cartographer

#### Barbarian
**Reference:** http://dnd2024.wikidot.com/barbarian:main
- **Primary Ability:** Strength
- **Hit Die:** d12
- **Key Features:**
  - Rage (2+ uses, increases damage resistance and damage output)
  - Reckless Attack (Advantage with drawback)
  - Extra Attack (Level 5)
  - Brutal Strike (Level 9+)
  - Subclasses: Path of the Berserker, Path of the Wild Heart, Path of the World Tree, Path of the Zealot

#### Bard
**Reference:** http://dnd2024.wikidot.com/bard:main
- **Primary Ability:** Charisma
- **Hit Die:** d8
- **Key Features:**
  - Bardic Inspiration (d6+, increases with level)
  - Spellcasting (Prepared spells from Bard list)
  - Expertise (2 skills at level 1, +2 at level 9)
  - Jack of All Trades (Level 2)
  - Magical Secrets (Level 10 - access to Cleric, Druid, Wizard spells)
  - Subclasses: College of Dance, College of Glamour, College of Lore, College of the Moon, College of Valor

#### Cleric
**Reference:** http://dnd2024.wikidot.com/cleric:main
- **Primary Ability:** Wisdom
- **Hit Die:** d8
- **Key Features:**
  - Spellcasting (Prepared spells from Cleric list)
  - Divine Order (Choose Protector or Thaumaturge at Level 1)
  - Channel Divinity (2 uses per rest at Level 2)
  - Blessed Strikes (Level 7)
  - Divine Intervention (Level 10)
  - Subclasses: Knowledge Domain, Life Domain, Light Domain, Trickery Domain, War Domain

#### Druid
**Reference:** http://dnd2024.wikidot.com/druid:main
- **Primary Ability:** Wisdom
- **Hit Die:** d8
- **Key Features:**
  - Spellcasting (Prepared spells from Druid list)
  - Druidic (Secret language)
  - Wild Shape (Level 2, becomes more powerful with levels)
  - Wild Companion (Level 2)
  - Elemental Fury (Level 7)
  - Beast Spells (Level 18)
  - Subclasses: Circle of the Land, Circle of the Moon, Circle of the Sea, Circle of the Stars

#### Fighter
**Reference:** http://dnd2024.wikidot.com/fighter:main
- **Primary Ability:** Strength or Dexterity
- **Hit Die:** d10
- **Key Features:**
  - Fighting Style (Choose a feat-based style)
  - Second Wind (d10 + level healing)
  - Weapon Mastery (3+ weapon types)
  - Action Surge (Extra action, 1-2 uses per rest)
  - Extra Attack (Level 5, increases to 3-4 attacks by level 20)
  - Indomitable (Level 9)
  - Subclasses: Banneret, Battle Master, Champion, Eldritch Knight, Psi Warrior

#### Monk
**Reference:** http://dnd2024.wikidot.com/monk:main
- **Primary Ability:** Dexterity
- **Hit Die:** d8
- **Key Features:**
  - Martial Arts (1d6+ damage, scales with level)
  - Unarmored Defense (AC = 10 + DEX + WIS mod)
  - Monk's Focus (Energy system for special abilities)
  - Unarmored Movement (Speed increases: +10 ft at level 2, up to +30 ft)
  - Stunning Strike (Level 5)
  - Evasion (Level 7)
  - Subclasses: Warrior of Mercy, Warrior of Shadow, Warrior of the Elements, Warrior of the Open Hand

#### Paladin
**Reference:** http://dnd2024.wikidot.com/paladin:main
- **Primary Ability:** Strength
- **Hit Die:** d10
- **Key Features:**
  - Lay On Hands (Healing pool: 5 × level HP)
  - Spellcasting (Prepared spells from Paladin list)
  - Weapon Mastery
  - Fighting Style (Level 2)
  - Paladin's Smite (Bonus damage with spell slots)
  - Channel Divinity (Level 3)
  - Extra Attack (Level 5)
  - Aura of Protection (Level 6+)
  - Subclasses: Oath of Devotion, Oath of Glory, Oath of the Ancients, Oath of the Noble Genies, Oath of Vengeance

#### Ranger
**Reference:** http://dnd2024.wikidot.com/ranger:main
- **Primary Ability:** Dexterity & Wisdom
- **Hit Die:** d10
- **Key Features:**
  - Spellcasting (Prepared spells from Ranger list)
  - Favored Enemy (Hunter's Mark, 2+ free uses)
  - Weapon Mastery
  - Deft Explorer (Level 2)
  - Fighting Style (Level 2)
  - Extra Attack (Level 5)
  - Roving (Level 6, climb/swim speeds)
  - Expertise (Level 9)
  - Subclasses: Beast Master, Fey Wanderer, Gloom Stalker, Hunter, Winter Walker

#### Rogue
**Reference:** http://dnd2024.wikidot.com/rogue:main
- **Primary Ability:** Dexterity
- **Hit Die:** d8
- **Key Features:**
  - Expertise (2 skills at level 1, +2 at level 6)
  - Sneak Attack (1d6+, scales to 10d6 at level 20)
  - Thieves' Cant (Secret language)
  - Weapon Mastery
  - Cunning Action (Bonus action to Dash, Disengage, Hide)
  - Steady Aim (Level 3)
  - Cunning Strike (Level 5+, customize Sneak Attack with effects)
  - Uncanny Dodge (Level 5)
  - Evasion (Level 7)
  - Subclasses: Arcane Trickster, Assassin, Scion of the Three, Soulknife, Thief

#### Sorcerer
**Reference:** http://dnd2024.wikidot.com/sorcerer:main
- **Primary Ability:** Charisma
- **Hit Die:** d6
- **Key Features:**
  - Spellcasting (Prepared spells from Sorcerer list)
  - Innate Sorcery (Enhanced spellcasting for 1 minute, 2 uses)
  - Font of Magic (Sorcery Points to create spell slots)
  - Metamagic (2 options at level 2, +2 at levels 10 & 17)
  - Sorcerous Restoration (Level 5)
  - Subclasses: Aberrant Sorcery, Clockwork Sorcery, Draconic Sorcery, Spellfire Sorcery, Wild Magic Sorcery

#### Warlock
**Reference:** http://dnd2024.wikidot.com/warlock:main
- **Primary Ability:** Charisma
- **Hit Die:** d8
- **Key Features:**
  - Eldritch Invocations (1+ special abilities)
  - Pact Magic (Limited spell slots that regain on Short Rest)
  - Magical Cunning (Level 2)
  - Contact Patron (Level 9)
  - Mystic Arcanum (Level 11+)
  - Subclasses: Archfey Patron, Celestial Patron, Fiend Patron, Great Old One Patron

#### Wizard
**Reference:** http://dnd2024.wikidot.com/wizard:main
- **Primary Ability:** Intelligence
- **Hit Die:** d6
- **Key Features:**
  - Spellcasting (Prepared spells from Wizard spell list)
  - Spellbook (Must study to prepare spells)
  - Ritual Adept (Cast ritual spells without preparing)
  - Arcane Recovery (Short Rest spell slot recovery)
  - Scholar (Level 2)
  - Memorize Spell (Level 5)
  - Spell Mastery (Level 18)
  - Signature Spells (Level 20)
  - Subclasses: Abjurer, Bladesinger, Diviner, Evoker, Illusionist

---

## Spellcasting

**Reference:** http://dnd2024.wikidot.com/spell:all

### Spell Schools
- Abjuration (Protection & banishment)
- Conjuration (Summoning & creation)
- Divination (Knowledge & information)
- Enchantment (Mind control & charm)
- Evocation (Damage & force)
- Illusion (Deception & phantasms)
- Necromancy (Death & undeath)
- Transmutation (Alteration & transformation)

### Sample Cantrips (0-Level Spells)
- **Acid Splash** (Evocation) - Ranged acid damage
- **Blade Ward** (Abjuration) - Resistance to damage
- **Fire Bolt** (Evocation) - Ranged fire damage
- **Guidance** (Divination) - Help with checks
- **Light** (Evocation) - Create light
- **Mage Hand** (Conjuration) - Invisible servant
- **Prestidigitation** (Transmutation) - Minor effects
- **Shocking Grasp** (Evocation) - Melee electric damage
- **Spare the Dying** (Necromancy) - Stabilize dying creature
- **True Strike** (Divination) - Automatic hit on next attack

---

## Species & Subclasses

### To Be Documented

This section will be expanded as specific species/ancestry pages are provided. Key categories to document:

- Humanoid Species (Humans, Elves, Dwarves, etc.)
- Fantasy Species (Dragonborn, Tieflings, etc.)
- Uncommon Species (Gnomes, Halflings, etc.)
- Subclass Options (Will be linked when species pages are available)

**Note:** To add more comprehensive species and subclass documentation, please provide:
- Links to each specific species page on the wiki
- Links to each subclass page (e.g., Barbarian subclass options)

---

## Combat & Rules

### Key Combat Mechanics
- **Initiative:** Based on Dexterity modifier
- **Action Economy:** Action, Bonus Action, Reaction per turn
- **Attack Roll:** d20 + modifier vs. AC
- **Damage:** Roll damage dice + modifier
- **Saving Throws:** d20 + modifier vs. spell/ability DC
- **Advantage/Disadvantage:** Roll twice, take higher/lower

### Conditions
Common conditions that affect gameplay:
- Blinded
- Charmed
- Deafened
- Exhaustion
- Frightened
- Grappled
- Incapacitated
- Invisible
- Paralyzed
- Petrified
- Poisoned
- Prone
- Restrained
- Stunned
- Unconscious

### Ability Scores & Modifiers
- Strength (STR) - Physical power
- Dexterity (DEX) - Reflexes & agility
- Constitution (CON) - Endurance & health
- Intelligence (INT) - Reasoning & memory
- Wisdom (WIS) - Awareness & insight
- Charisma (CHA) - Force of personality

Each score contributes a modifier: (score - 10) ÷ 2

---

## Implementation Notes for AI Coder

When implementing game mechanics:

1. **Class Features** should scale with character level as specified in the class tables
2. **Spellcasting** rules vary by class:
   - **Prepared Casters** (Artificer, Cleric, Druid, Paladin, Ranger, Wizard): Choose spells from list
   - **Known Casters** (Bard, Sorcerer, Warlock): Learn fewer spells
3. **Bastions** unlock at level 5 and expand with level milestones
4. **Weapon Mastery** provides special attack properties based on weapon selection
5. **Subclasses** grant features at levels 3, 6, 10, 14, 15, 18, and 20 depending on the class

---

## Quick Links to Major Content

| Content | Link |
|---------|------|
| Bastions (Base Building) | http://dnd2024.wikidot.com/bastions |
| Artificer | http://dnd2024.wikidot.com/artificer:main |
| Barbarian | http://dnd2024.wikidot.com/barbarian:main |
| Bard | http://dnd2024.wikidot.com/bard:main |
| Cleric | http://dnd2024.wikidot.com/cleric:main |
| Druid | http://dnd2024.wikidot.com/druid:main |
| Fighter | http://dnd2024.wikidot.com/fighter:main |
| Monk | http://dnd2024.wikidot.com/monk:main |
| Paladin | http://dnd2024.wikidot.com/paladin:main |
| Ranger | http://dnd2024.wikidot.com/ranger:main |
| Rogue | http://dnd2024.wikidot.com/rogue:main |
| Sorcerer | http://dnd2024.wikidot.com/sorcerer:main |
| Warlock | http://dnd2024.wikidot.com/warlock:main |
| Wizard | http://dnd2024.wikidot.com/wizard:main |
| Spells (All) | http://dnd2024.wikidot.com/spell:all |

---

## Document Status

**Created:** February 9, 2026  
**Coverage:** D&D 2024 Core Classes, Bastions, Spellcasting, Spell Lists  
**Pending:** Species/Species options, complete subclass details, combat rules detail

**Last Updated:** [Check document for date]
