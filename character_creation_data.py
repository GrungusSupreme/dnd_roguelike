"""Data and helpers for character creation UI."""

ALL_SKILLS = [
    "Acrobatics",
    "Animal Handling",
    "Arcana",
    "Athletics",
    "Deception",
    "History",
    "Insight",
    "Intimidation",
    "Investigation",
    "Medicine",
    "Nature",
    "Perception",
    "Performance",
    "Persuasion",
    "Religion",
    "Sleight of Hand",
    "Stealth",
    "Survival",
]

CLASS_SKILL_OPTIONS = {
    "Barbarian": [
        "Animal Handling",
        "Athletics",
        "Intimidation",
        "Nature",
        "Perception",
        "Survival",
    ],
    "Bard": ALL_SKILLS,
    "Cleric": ["History", "Insight", "Medicine", "Persuasion", "Religion"],
    "Druid": [
        "Animal Handling",
        "Arcana",
        "Insight",
        "Medicine",
        "Nature",
        "Perception",
        "Religion",
        "Survival",
    ],
    "Fighter": [
        "Acrobatics",
        "Animal Handling",
        "Athletics",
        "History",
        "Insight",
        "Intimidation",
        "Persuasion",
        "Perception",
        "Survival",
    ],
    "Monk": ["Acrobatics", "Athletics", "History", "Insight", "Religion", "Stealth"],
    "Paladin": ["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"],
    "Ranger": [
        "Animal Handling",
        "Athletics",
        "Insight",
        "Investigation",
        "Nature",
        "Perception",
        "Stealth",
        "Survival",
    ],
    "Rogue": [
        "Acrobatics",
        "Athletics",
        "Deception",
        "Insight",
        "Intimidation",
        "Investigation",
        "Perception",
        "Persuasion",
        "Sleight of Hand",
        "Stealth",
    ],
    "Sorcerer": ["Arcana", "Deception", "Insight", "Intimidation", "Persuasion", "Religion"],
    "Warlock": ["Arcana", "Deception", "History", "Intimidation", "Investigation", "Nature", "Religion"],
    "Wizard": ["Arcana", "History", "Insight", "Investigation", "Medicine", "Nature", "Religion"],
}

CLASS_SKILL_COUNTS = {
    "Barbarian": 2,
    "Bard": 3,
    "Cleric": 2,
    "Druid": 2,
    "Fighter": 2,
    "Monk": 2,
    "Paladin": 2,
    "Ranger": 3,
    "Rogue": 4,
    "Sorcerer": 2,
    "Warlock": 2,
    "Wizard": 2,
}

ABILITY_CODES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

ORIGIN_FEAT_OPTIONS = [
    "Alert",
    "Magic Initiate (Cleric)",
    "Magic Initiate (Druid)",
    "Magic Initiate (Wizard)",
    "Savage Attacker",
    "Skilled",
    "Crafty",
    "Healthy",
    "Iron Fist",
    "Meaty",
]

ORIGIN_FEAT_REPEATABLE_EXACT = {"Skilled"}
ORIGIN_FEAT_REPEATABLE_PREFIXES = ("Magic Initiate",)

TOOL_PROFICIENCY_OPTIONS = [
    "Alchemist's Supplies",
    "Brewer's Supplies",
    "Calligrapher's Supplies",
    "Carpenter's Tools",
    "Cartographer's Tools",
    "Cobbler's Tools",
    "Cook's Utensils",
    "Glassblower's Tools",
    "Jeweler's Tools",
    "Leatherworker's Tools",
    "Mason's Tools",
    "Painter's Supplies",
    "Potter's Tools",
    "Smith's Tools",
    "Tinker's Tools",
    "Weaver's Tools",
    "Woodcarver's Tools",
    "Disguise Kit",
    "Forgery Kit",
    "Herbalism Kit",
    "Navigator's Tools",
    "Poisoner's Kit",
    "Thieves' Tools",
    "Dice Set",
    "Dragonchess Set",
    "Playing Card Set",
    "Three-Dragon Ante Set",
    "Musical Instrument",
]

SPECIES_OPTIONS = [
    "Dragonborn",
    "Dwarf",
    "Elf",
    "Gnome",
    "Goliath",
    "Halfling",
    "Human",
    "Orc",
    "Tiefling",
]

SPECIES_SPEED_FEET = {
    "Dragonborn": 30,
    "Dwarf": 30,
    "Elf": 30,
    "Gnome": 30,
    "Goliath": 35,
    "Halfling": 30,
    "Human": 30,
    "Orc": 30,
    "Tiefling": 30,
}

SPECIES_TRAIT_CHOICES = {
    "Dragonborn": {
        "Draconic Ancestry": [
            "Black (Acid)",
            "Blue (Lightning)",
            "Brass (Fire)",
            "Bronze (Lightning)",
            "Copper (Acid)",
            "Gold (Fire)",
            "Green (Poison)",
            "Red (Fire)",
            "Silver (Cold)",
            "White (Cold)",
        ],
    },
    "Elf": {
        "Elven Lineage": ["Drow", "High Elf", "Wood Elf"],
    },
    "Gnome": {
        "Gnomish Lineage": ["Forest Gnome", "Rock Gnome"],
    },
    "Goliath": {
        "Giant Ancestry": [
            "Cloud",
            "Fire",
            "Frost",
            "Hill",
            "Stone",
            "Storm",
        ],
    },
    "Tiefling": {
        "Fiendish Legacy": ["Abyssal", "Chthonic", "Infernal"],
        "Size": ["Medium", "Small"],
    },
    "Human": {
        "Size": ["Medium", "Small"],
    },
}

POINT_BUY_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}


def point_buy_cost(score: int) -> int:
    if score < 8 or score > 15:
        raise ValueError("score must be between 8 and 15")
    return POINT_BUY_COSTS[score]


def point_buy_delta(current: int, target: int) -> int:
    return point_buy_cost(target) - point_buy_cost(current)
