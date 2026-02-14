# Game Design Vision - Long Term Development

**Status:** Design Phase - Not Yet Implemented  
**Last Updated:** 2026-02-10  
**Current Version:** 0.5 (Wave Defense Prototype)  
**Target Version:** 2.0+ (Kingdom Defense Roguelike)

---

## Overview

Transform the current wave-based tactical combat game into a comprehensive kingdom management roguelike where players defend their keep against raids while building up infrastructure, managing resources, and recruiting NPCs over the course of months and years.

**Core Pillars:**
1. **Tactical Combat** - D&D 5.5e SRD-based combat on tactical grid
2. **Kingdom Management** - Build and upgrade keep, manage resources
3. **Narrative Events** - Random events with skill checks and choices
4. **Time Management** - Balance raids, resting, crafting, and building
5. **NPC Systems** - Recruit specialists to automate and enhance activities

---

## Main Non-Combat Loop

### Calendar System

**Structure:**
- Game divided into **Months**
- Each month contains **Days** (exact number TBD, suggest 28-30)
- Each day acts as a **turn** with "End Day" button

**Daily Activities:**
Players can experience one of the following per day:
1. **Raid Day** - Combat encounter(s) against enemy waves
2. **Long Rest Day** - Dedicated rest to recover resources
3. **Event Day** - Random narrative event with choices/skill checks
4. **Free Day** - Crafting, trading, farming, or building activities

### Raid Scheduling

**Raid Frequency:**
- Number of raids per month determined by:
  - Player level (higher level = more frequent raids)
  - Keep threat level (upgrades may attract attention)
  - Story progression flags
  - Random variation

**Raid Forecasting:**
- Base: Raids occur on random days with no warning
- Improvements available via:
  - Skill proficiencies (Perception, Survival)
  - Class abilities (Ranger features, Divination magic)
  - Keep upgrades (watchtowers, scouts)
  - NPC specialists (scouts, diviners, or similar roles)

**Example Progression:**
- Level 1-3: 2-3 raids per month, no forecasting
- Level 4-6: 3-4 raids per month, 1-day warning with upgrades
- Level 7-9: 4-5 raids per month, 2-3 day warning with upgrades
- Level 10+: 5-6 raids per month, up to 5-day warning with full forecasting

### Rest Mechanics

**Long Rest:**
- Requires a **full day** with no raid
- Can only be taken if no raid occurs that day
- If player has recently taken long rest and not been raided, they remain "rested" (no time spent)
- Restores: HP, spell slots, class feature uses, removes exhaustion levels

**Short Rest:**
- Can be taken **between multiple raids** on the same day
- Takes no calendar time (abstracted as moments between encounters)
- Restores: Some class features, Hit Dice healing, some spell slots (Warlock)

**Exhaustion:**
- Players going extended periods without long rest accumulate exhaustion
- SRD 5.2.1 exhaustion rules apply:
  - Level 1: Disadvantage on ability checks
  - Level 2: Speed halved
  - Level 3: Disadvantage on attack rolls and saving throws
  - Level 4: HP maximum halved
  - Level 5: Speed reduced to 0
  - Level 6: Death

**Exhaustion Threshold (Balanced for Gameplay):**
- 4-5 consecutive raid days without long rest = 1 exhaustion level
- 7-8 consecutive raid days = 2 exhaustion levels
- 10+ consecutive raid days = 3+ exhaustion levels
- **Clear warning system**: UI indicator at 3 raid days ("Rest Recommended")
- Flashing warning at 4 raid days ("Exhaustion Risk!")
- Note: More lenient than strict 5e to allow strategic play

### Random Events System

**Event Triggers:**
- Occur on days with **no raid** and **no long rest needed**
- Chance-based system (suggest 30-50% chance per eligible day)
- Events do NOT consume the entire day - player can still do other activities after resolving event

**Event Types:**
1. **Narrative Choice** - Make decision, receive rewards/consequences
2. **Skill Check** - Roll skill to determine outcome
3. **NPC Arrival** - Potential recruit with skill check to convince them to stay
4. **Crisis** - Requires immediate resource expenditure or risk penalty
5. **Opportunity** - Limited-time trade, quest hook, or bonus

**Event Weighting:**
Events should favor player's:
- **Class** - Rogues get crime events, Clerics get religious events
- **Background** - Criminals get underworld contacts, Soldiers get military events
- **Proficiencies** - Events should utilize skills player is trained in
- **Current Needs** - More NPC events if keep is understaffed

**Event Content Strategy:**
- **Phase 4 Launch:** 30 well-written, high-quality events (foundation)
- **Modular Design:** Mix-and-match components to create variations
- **Iterative Expansion:** Add 5-10 new events per update/patch
- **Community Content:** Consider tools for player-created events later

**Example Event:**
```
Event: "Suspicious Merchant"
Class Weight: Rogue (high), Warlock (medium), Paladin (low)

A cloaked merchant arrives offering rare items at suspiciously low prices.

Choices:
[Investigate (Investigation DC 13)] - Learn if goods are stolen
[Buy Everything (100 GP)] - Acquire items but risk reputation
[Turn Away] - Safe but miss opportunity
[Intimidate (Intimidation DC 15)] - Force merchant to reveal source

Outcomes vary based on choice and skill check results
```

### Free Day Activities

On days with no raids, no mandatory rest, and no events (or after event resolution), players can:

1. **Crafting** - Create items using resources and tool proficiencies
2. **Trading** - Buy/sell at merchant NPCs or traveling traders
3. **Farming** - Tend crops, harvest resources
4. **Building** - Upgrade keep or construct new facilities
5. **Research** - Study spells, improve recipes, unlock blueprints
6. **Training** - Improve NPC capabilities or unlock new features
7. **Scouting** - Gather intelligence on upcoming threats (skill check)

---

## Skill Integration & Character Depth

### Skill Checks Beyond Combat

**Skills now affect strategic gameplay:**

- **Scouting** - Perception/Survival checks to forecast raids or enemy composition
- **Research** - Arcana/History checks to unlock better crafting recipes
- **Crafting** - Appropriate tool proficiency + ability check to create items
- **Events** - All skills can appear in narrative events
- **NPC Recruitment** - Persuasion/Intimidation/Deception to recruit or negotiate
- **Resource Gathering** - Nature/Survival to improve yields

### Tool Proficiencies

**Active Mechanical Benefits:**

- **Smith's Tools** - Craft/repair weapons and armor, upgrade keep defenses
- **Alchemist's Supplies** - Craft potions and bombs
- **Carpenter's Tools** - Build structures, traps, and siege equipment
- **Mason's Tools** - Upgrade keep walls and fortifications
- **Cook's Utensils** - Preserve food longer, create rations efficiently
- **Herbalism Kit** - Craft healing items, identify useful plants
- **Thieves' Tools** - Create traps, improve treasure yields from raids

**Proficiency Benefits:**
- Reduced time cost for related activities
- Higher quality results (better stats on crafted items)
- Can create advanced recipes (unproficient players limited to basic)
- Bonus to NPC productivity when supervising related work

### Backgrounds (SRD Only)

Use the SRD backgrounds (Acolyte, Criminal, Sage, Soldier) during phase 2. Backgrounds provide the SRD-defined ability score choices, origin feat, skill/tool proficiencies, and starting equipment. No additional passive bonuses are planned for phase 2; homebrew background bonuses are deferred.

---

## Keep & Territory Management

### The Keep Structure

**Core Functions:**
1. **Storage** - Houses gold, resources, items, and equipment
2. **Protection** - Defensive structure that enemies must breach
3. **Housing** - Provides shelter for player and NPCs
4. **Production** - NPC workstations and crafting facilities

**Keep Layout:**
- Central **8×8 keep building** (existing combat arena)
- **Surrounding territory** on 64×64 grid (existing map size)
- Default: Keep positioned on **small hill** (high ground advantage)
- Future: Possibly randomized terrain generation

### Keep Upgrades

**Upgrade Categories:**

**1. Defensive Upgrades**
- **Walls** - Increase HP, AC, and enemy pathing difficulty
- **Towers** - Provide elevated positions for archers (player or NPC)
- **Gates** - Reinforced doors with higher breakthrough threshold
- **Traps** - Damage enemies on approach (require maintenance)
- **Moat** - Slows enemy movement, prevents some enemy types

**2. Functional Upgrades**
- **Storage Expansion** - Increase max capacity for resources/items
- **Workshops** - Enable advanced crafting, reduce crafting time
- **Barracks** - House more NPCs, improve guard effectiveness
- **Farms** - Increase food production capacity
- **Market Stall** - Attract traveling merchants more frequently

**3. Special Upgrades**
- **Library** - Research faster, unlock secret recipes
- **Temple** - Enhance healing, remove curses, divine forecasting
- **Armory** - Store more equipment, improve gear quality
- **Watchtower** - Increase raid forecasting range
- **Training Ground** - Improve NPC combat effectiveness

**Upgrade Costs:**

**Option A: Player Crafting**
- Cost: Raw resources (wood, stone, metal)
- Time: Multiple days depending on complexity
- Requirement: Appropriate tool proficiency (Carpenter, Mason, Smith)
- Benefit: Free labor, personal touch

**Option B: NPC Construction**
- Cost: Gold + raw resources
- Time: Faster than player (1-2 days for most upgrades)
- Requirement: Builder NPC in residence
- Benefit: Player free to do other activities

**Example Upgrade:**
```
Stone Wall Reinforcement
- Resources: 200 Stone, 50 Wood (scaffolding)
- Player Time: 5 days (Mason's Tools proficiency required)
- NPC Time: 2 days + 400 GP (Builder required)
- Effect: Keep door HP +50, AC +2, enemy breach DC +3
```

### Surrounding Territory

**Territory Types:**

**1. Resource Production**
- **Farms** - Grow food (wheat, vegetables, herbs)
- **Orchards** - Grow fruit (slower growth, higher value)
- **Forest** - Harvest wood for construction
- **Quarry** - Extract stone for building
- **Mine** - Extract metal ore for crafting

**Production Mechanics:**
- Each tile dedicated to production yields resources per day
- Yield affected by:
  - Tile quality (randomized at world gen)
  - NPC bonuses (Farmhand NPC = +50% to adjacent farm tiles)
  - Upgrades (Irrigation system, better tools)

**2. Defensive Preparations**
- **Trenches** - Slow enemy movement, provide cover
- **Spike Pits** - Damage enemies, low HP enemies may die instantly
- **Barricades** - Funnel enemies into kill zones
- **Caltrops** - Damage and slow, require replenishing after raids
- **Oil Pots** - Create fire zones (persistent damage area)

**Design Philosophy:**
- Defensive structures require maintenance (gold/resources after raids)
- Balance: Too many defenses = trivial combat (avoid tower defense mode)
- Enemies adapt to repeated strategies (destroy common traps)

### Terrain & Positioning

**High Ground Advantage:**
- Keep on hill: Player gets +1 to attack rolls when elevated
- Elevation rules from 5e: High ground = advantage on melee attacks from above

**Future Consideration:**
- Randomized terrain at game start (hills, rivers, forests)
- Affects strategy and build planning
- Deferred to later development phase

---

## Economy & Resources

### Currency: Gold

**Gold Sources:**
- Enemy kills (all enemies drop gold based on type)
- Selling resources/crafted items
- Event rewards
- Treasure from major raid victories

**Gold Sinks:**
- Purchasing food
- Hiring NPCs
- Buying rare resources or items from merchants
- NPC-automated construction costs
- Maintenance costs for advanced keep upgrades

### Crafting Resource: Scrap

**Scrap Tiers:**
1. **Common Scrap** - 50% drop rate, used for basic gear
2. **Uncommon Scrap** - 25% drop rate, used for good gear
3. **Rare Scrap** - 15% drop rate, used for excellent gear
4. **Legendary Scrap** - 5% drop rate, used for best-in-slot gear

**Drop Mechanics:**
- Each killed enemy has chance to drop scrap
- Tier determined by:
  - Enemy type (bosses drop better scrap)
  - Player level (higher level = slightly better drops)
  - Background bonuses (potential future feature)

**Scrap Uses:**
- Combine scrap + other resources to craft items
- Example: Common Scrap (5) + Iron Ore (2) = Longsword
- Example: Rare Scrap (2) + Dragon Scale (1) = +2 Dragonscale Armor

### Essential Resource: Food

**Food Requirement:**
- Player requires 1 food per long rest
- Each NPC requires 1 food per day (flat rate regardless of activity)
- No food = cannot take long rest = exhaustion risk

**Food Sources:**
1. **Farming** - Primary source, sustainable, slow ramp-up
2. **Purchasing** - Immediate but expensive, emergency option
3. **Hunting/Foraging** - Random event rewards, unreliable
4. **Trading** - Sell other resources to buy food

**Food Types:**
- **Rations** (basic) - 1 GP each, fulfills requirement
- **Prepared Meals** (with Cook's Utensils) - 2 GP value, improves morale
- **Preserved Food** - Lasts longer in storage, requires Cook proficiency

**Implementation Approach:**
- **Monthly Food Budget System** - Track food as monthly consumption vs production
- Player sees: "Food Supply: 45/60 (15 days remaining)"
- Warning at 10 days remaining, critical warning at 5 days
- Avoids tedious daily micromanagement while maintaining resource pressure
- Auto-purchase option available for players with sufficient gold

### Production Resources

**Resources from Territory:**
- **Wood** - From forest tiles, used in most construction
- **Stone** - From quarry tiles, used in defensive structures
- **Iron Ore** - From mine tiles, used in weapons/armor
- **Herbs** - From farm tiles, used in alchemy
- **Leather** - From hunting (events), used in light armor

**Resource Management:**
- All resources stored in keep (capacity-limited)
- Can be:
  - Used for crafting
  - Used for keep upgrades
  - Sold for gold
- Production rate: X resources per day from each dedicated tile

**Example Resource Costs:**
```
Longsword (Crafting):
- Common Scrap: 5
- Iron Ore: 3
- Wood: 1 (for handle)
- Time: 1 day (Smith's Tools required)

Wooden Palisade (Keep Upgrade):
- Wood: 150
- Iron Ore: 10 (nails/braces)
- Time: 3 days (Carpenter's Tools) OR 1 day + 200 GP (NPC)
```

---

## NPC System

### NPC Acquisition

**Method 1: Event Recruitment**
- NPC arrives via random event
- Player must pass skill check to convince them to stay
- Skill varies: Persuasion, Intimidation, Deception, or class-specific (Performance for Bard)
- Harder checks = better NPCs
- Free if successful

**Method 2: Hiring**
- Spend gold to recruit NPC from traveling merchant or marketplace
- No skill check required
- Cost scales with NPC quality: 500-5000 GP
- Guaranteed specific specialization

### NPC Roles

**Production Specialists:**
- **Farmer** - +50% yield to adjacent farm tiles, reduces food costs
- **Lumberjack** - +50% yield to forest tiles
- **Miner** - +50% yield to mine/quarry tiles
- **Herbalist** - Gathers herbs daily, crafts basic potions autonomously

**Crafting Specialists:**
- **Blacksmith** - Automates weapon/armor crafting, unlocks advanced recipes
- **Alchemist** - Automates potion crafting, experiments for new formulas
- **Carpenter** - Automates building construction, reduces construction time 50%
- **Mason** - Specializes in stone structures, improves defense value

**Support Specialists:**
- **Merchant** - Provides daily shop (buy/sell without waiting for events)
- **Scholar** - Provides research bonuses, teaches player new proficiencies
- **Bard** - Provides AoE buff to player (+1 to all rolls during raids)
- **Priest** - Provides free healing after raids, removes curses/diseases

**Combat Support (LIMITED):**
- **Archer Guard** - Can be stationed in upgraded tower, attacks enemies (max 2-3)
- **Gate Guard** - Defends keep door, buys time for player (max 1-2)
- **Patrol** - Provides early warning, increases forecasting (max 1)

**Design Principle:**
- Combat NPCs should be **helpers**, not replacements for player
- Strict caps on combat NPC count
- Combat NPCs weaker than player character
- Purpose: Manage trash mobs, give player tactical options, not trivialize combat

### NPC Management

**Maintenance:**
- Each NPC requires 1 food per day
- No gold upkeep (already paid during hiring)
- NPCs can leave if mistreated (run out of food, keep destroyed, specific event choices)

**Benefits:**
- Automate tedious tasks (resource gathering, basic crafting)
- Unlock capabilities player lacks (wrong tool proficiencies)
- Provide passive bonuses (inspiration, shop access, healing)
- Enable player to focus on strategic decisions and combat

**Limitations:**
- NPCs vulnerable during raids (can be killed if keep breached)
- Player must balance NPC count vs food consumption
- Each NPC type limited (can't have 10 blacksmiths)

---

## Enemy Behavior & AI

### Basic Enemy AI

**Default Behavior:**
- **Beeline to Keep** - Shortest path to keep door
- **Attack on Contact** - Attack player if player blocks path
- **Breach Attempts** - Attack keep door if reached

**Pathing Priority:**
1. If player is adjacent → attack player
2. If path to keep door is clear → move toward door
3. If obstacle blocks path → attack obstacle OR path around it
4. If at door → attack door until breached

### Advanced Enemy Behavior

**"Hiding Too Long" Mechanic:**

If player remains inside keep for extended period, enemies escalate:

**Escalation Stages (Specific Turn Counts):**
1. **Rounds 1-4:** Normal behavior, attack door
2. **Rounds 5-7:** Start targeting surrounding structures (farms, workshops)
3. **Round 7:** ⚠️ Warning message: "Enemies are gathering materials..."
4. **Rounds 8-9:** Set fires to resource-producing tiles
5. **Round 10:** 🚨 **Siege equipment construction begins** (visual indicator)
6. **Round 12+:** Siege equipment operational, attacking keep

**Siege Equipment (Intelligent Enemies Only):**
- **Ladders** (Round 10) - Scale walls, attack from elevated positions
- **Battering Ram** (Round 12) - +5 damage per hit to keep door
- **Trebuchet** (Round 15) - Long-range attacks on keep interior (can hit player indoors)
- **Fire Arrows** (Round 13) - Ignite wooden structures

**Design Purpose:**
- Prevent "turtle in keep forever" strategy
- Force player to engage actively
- Create tension and urgency with clear warnings
- Reward aggressive, proactive play
- Fair: Player has 7+ rounds to adjust strategy before siege begins

### Enemy Staging Area

**Tree Line:**
- Enemies spawn at edge of 64×64 map
- Tree line provides cover (+2 AC from cover bonus)
- Player cannot cross tree line (invisible boundary)
- Player cannot build/clear trees in tree line

**Visibility:**
- Player has limited vision into tree line
- With Perception checks or Watchtower: Can see enemy composition
- With advanced scouting: Can see enemy count and types before raid begins

**Tactical Implications:**
- Enemies can rally and organize before attacking
- Player can prepare if they scout successfully
- Adds reconnaissance layer to gameplay

---

## Grid & Movement System

### Standard 5e Grid (Traditional)

**Grid Structure:**
- **64×64 grid of squares** (existing map size)
- Each square = 5 feet × 5 feet
- Characters **occupy squares**, not intersection points
- Follows standard D&D 5e grid rules

**Movement Rules:**
- **Diagonal Movement:** Use simplified 5e rule - every square costs 5 ft (including diagonals)
  - Alternative: Use variant 5/10/5 rule (first diagonal = 5 ft, second = 10 ft, alternating)
  - Recommend simplified for ease of play
- Characters move from square to adjacent square (orthogonal or diagonal)
- Speed determines how many squares per turn (30 ft speed = 6 squares)

**Technical Implementation:**
- Character position: (x, y) represents square coordinates (0-63 in each axis)
- Adjacent squares: 8 directions (N, NE, E, SE, S, SW, W, NW)
- Distance calculation: Simplified Chebyshev (max of |Δx|, |Δy|) × 5 ft

**Example:**
```
Character at (10, 10) with 30 ft speed can move to:
- Adjacent: (11, 10), (10, 11), (11, 11), etc. (5 ft each)
- Can move up to 6 squares away in one turn
```

### Cover & Line of Sight

**Standard 5e Rules:**
- Cover determined by obstacles between attacker square and target square
- Trace line from center of attacker's square to center of target's square
- If line passes through obstacle → target has cover
  - **Half Cover:** +2 AC, +2 DEX saves (low wall, furniture)
  - **Three-Quarters Cover:** +5 AC, +5 DEX saves (portcullis, thick tree)
  - **Total Cover:** Cannot be targeted directly (full wall)

**Obstacles Providing Cover:**
- Keep walls (three-quarters or total)
- Trees (half or three-quarters)
- Defensive structures (barricades = half, stone walls = three-quarters)
- Other creatures (half cover if medium, three-quarters if large)

---

## Implementation Phasing

### ⚠️ CRITICAL: Phase Discipline

**MANDATORY RULE:** Each phase must be **fully playable, fun, and balanced** before moving to the next phase. No exceptions.

**Between-Phase Checklist:**
- [ ] All features for current phase implemented
- [ ] Comprehensive playtesting completed (minimum 2-3 hours of gameplay)
- [ ] Balance issues identified and addressed
- [ ] No game-breaking bugs remain
- [ ] Documentation updated (CHANGELOG, ROADMAP)
- [ ] User experience feels good (not tedious or frustrating)
- [ ] "Would I play this for fun?" test passes

**If any item fails:** Fix it before proceeding. Do not add new features to incomplete phases.

---

### Phase 1: Core Combat (CURRENT - v0.5)
✅ Already complete

### Phase 2: Feature Integration (v0.6-0.8)
**Implementation:** 2-3 development sessions  
**Playtesting Required:** 3-5 hours before Phase 3

- Integrate class features into combat
- Add ranged combat
- Expand enemy variety
- Status effects
- Equipment system

### Phase 3: Calendar & Rest System (v0.9-1.0)
**Implementation:** 1-2 sessions  
**Playtesting Required:** 2-3 hours before Phase 4

- Implement day/month calendar
- Long rest / short rest mechanics
- Exhaustion tracking (4-5 raid threshold)
- Basic raid scheduling

### Phase 4: Event System (v1.1-1.3)
**Implementation:** 2-3 sessions  
**Playtesting Required:** 3-4 hours before Phase 5

- Random event framework
- Skill check integration
- 30 high-quality event templates (foundation)
- Event weighting based on class/background

### Phase 5: Keep & Territory (v1.4-1.6)
**Implementation:** 3-4 sessions  
**Playtesting Required:** 4-5 hours before Phase 6

- Keep upgrade system
- Territory tile assignment (farm/forest/mine/defense)
- Resource production mechanics
- Basic crafting system

### Phase 6: Economy & Resources (v1.7-1.8)
**Implementation:** 2 sessions  
**Playtesting Required:** 2-3 hours before Phase 7

- Full economy implementation (gold, scrap, food)
- Monthly food budget system (not daily tracking)
- Buy/sell system
- Resource management UI

### Phase 7: NPC System (v1.9-2.0)
**Implementation:** 3-4 sessions  
**Playtesting Required:** 4-5 hours before Phase 8

- NPC recruitment (events + hiring)
- NPC specialists and bonuses
- NPC management UI
- Limited combat NPCs (strict caps)

### Phase 8: Advanced Enemy AI (v2.1+)
**Implementation:** 2-3 sessions  
**Playtesting Required:** 3-4 hours before Phase 9

- Hiding escalation mechanics (specific turn counts: warning at Round 7, siege at Round 10)
- Siege equipment with visual indicators
- Tree line staging and scouting
- Enemy composition variety

### Phase 9: Polish & Balance (v2.2+)
**Implementation:** Ongoing  
**Playtesting Required:** Extensive

- Balance adjustments based on player feedback
- UI/UX improvements
- Performance optimization
- Bug fixes and quality of life features

---

## Design Concerns & Recommendations

### 🔴 Critical Concerns

**1. Scope Explosion**
- **Issue:** This is 10x more complex than current game
- **Risk:** Multi-year development, feature creep, burnout
- **Recommendation:**
  - Strict adherence to phased implementation
  - Each phase must be fully playable before moving to next
  - Be willing to cut features that don't work

- **Issue:** Food requirement for player + every NPC daily could be micromanagement hell
- **Risk:** Turns fun game into spreadsheet management
- **Resolution:** ✅ IMPLEMENTED
  - Monthly food budget system specified (see Economy section)
  - Warning at 10 days, critical at 5 days
  - Auto-purchase option for players with gold
  - No tedious daily tracking

### 🟡 Moderate Concerns

- **Issue:** Need hundreds of events to avoid repetition
- **Risk:** Players see same 10 events over and over
- **Resolution:** ✅ IMPLEMENTED
  - Phase 4 launches with 30 high-quality events (see Event section)
  - Modular design for variations
  - Iterative expansion (5-10 events per patch)
  - Community content tools considered for later

**5. NPC Automation Risk**
- **Issue:** Too much automation removes gameplay
- **Risk:** Player becomes passive observer
- **Recommendation:**
  - Good: Automation for tedious tasks (harvesting resources)
  - Bad: Automation for meaningful choices (combat, major crafting)
  - Maintain player as active protagonist, NPCs as support

- **Issue:** 5e exhaustion is VERY punishing (speed 0 at level 5, death at 6)
- **Risk:** Feels unfair, forces rest too often, limits strategic options
- **Resolution:** ✅ IMPLEMENTED
  - Lenient thresholds: 4-5 raid days before exhaustion level 1 (see Rest section)
  - Clear UI warnings at 3 days ("Rest Recommended"), flashing at 4 days
  - More forgiving than strict 5e rules
  - Items/NPCs that can mitigate exhaustion (future consideration)

### 🟢 Minor Concerns

**7. Siege Equipment Clarity**
- **Issue:** When exactly do enemies build siege equipment?
- **Risk:** Unclear rules, feels arbitrary
- **Recommendation:**
  - Define clear turn thresholds (e.g., "After 10 rounds inside keep")
  - Visual indicators (enemies building siege works)
  - Warning messages to player

**8. Resource Storage Complexity**
- **Issue:** Tracking gold, 4 scrap tiers, food, wood, stone, iron, herbs, leather...
- **Risk:** Overwhelming inventory management
- **Mitigation Strategies:**
  - Clear, organized UI with categories
  - Visual indicators for low supplies
  - Auto-sort and filtering options
  - Resource cap warnings
  - Requires UX testing in Phase 6

**9. Calendar Pacing**
- **Issue:** How many days per month? How fast does time pass?
- **Risk:** Too slow = grindy, too fast = no time to build
- **Recommendation:**
  - 28-30 days per month (familiar calendar)
  - Level 1-5: ~3 raids/month = plenty of free time
  - Level 6-10: ~5 raids/month = moderate pressure
  - Level 11+: ~7 raids/month = high intensity
  - Playtest extensively

---

## Summary of Design Goals

**What This Design Achieves:**
✅ Deep strategic layer (resource, time, NPC management)  
✅ Strong D&D integration (skills, backgrounds, tool proficiencies matter)  
✅ Replayability (random events, different backgrounds, different builds)  
✅ Player agency (many choices: offense vs defense, NPC hiring, crafting focus)  
✅ Satisfying progression (keep grows, character grows, systems unlock)

**What Requires Careful Implementation:**
⚠️ Balancing complexity vs tedium  
⚠️ Event content volume and variety  
⚠️ Resource management UI/UX  
⚠️ Preventing NPC over-automation

**What MUST Be Playtested Before Phase Completion:**

### Phase Playtest Checklists

**Phase 1: Core Combat**
- 3 full waves in both terminal and GUI
- Initiative, crits, defend, and potions behave as described
- No hard locks or stuck turns

**Phase 2: Feature Integration**
- Each class feature triggers correctly at least once
- Feature use feels impactful but not dominant
- Ranged combat and melee both feel viable
- Enemy variety creates different tactical choices

**Phase 3: Calendar & Rest System**
- Day/month pacing feels reasonable across 2-3 months
- Rest availability matches raid schedule without soft-locking
- Exhaustion thresholds feel fair and visible

**Phase 4: Event System**
- 30 events seen with low repetition over 2-3 months
- Skill checks produce meaningful outcomes
- Event weighting matches class/background expectations

**Phase 5: Keep & Territory**
- At least 3 different upgrade paths feel viable
- Territory choices meaningfully affect resource flow
- Building time/cost feels worth the payoff

**Phase 6: Economy & Resources**
- Monthly food budget is easy to understand and plan for
- Buy/sell prices feel reasonable across 2-3 months
- Resource caps create pressure without frustration

**Phase 7: NPC System**
- NPCs help without replacing the player
- Recruiting and managing NPCs is clear and not tedious
- NPC bonuses feel noticeable but balanced

**Phase 8: Advanced Enemy AI**
- Siege escalation timing is predictable and fair
- Warning at Round 7 is actionable, Round 10 escalation is readable
- AI variety creates new positioning choices

**Phase 9: Polish & Balance**
- 3+ hour run without major friction or crashes
- UI clarity holds up under long sessions
- Overall fun and replayability feel strong

---

## Next Steps

**DO NOT IMPLEMENT YET** - Current priority is Phase 2 (Feature Integration)

**When Ready to Begin Long-Term Features:**
1. Complete Phase 2 (class features, ranged combat, equipment)
2. Review this document and refine based on lesson learned
3. Start Phase 3 (calendar system) as first step toward broader vision
4. Implement one phase at a time, ensuring each is fun before moving on

**Documentation Updates:**
- ROADMAP.md updated to reference this vision
- ARCHITECTURE.md notes long-term structural needs
- Implementation begins only after Phase 2 complete

---

**Last Updated:** 2026-02-10  
**Status:** Design specification, awaiting Phase 2 completion before implementation
