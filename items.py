"""Item system for D&D roguelike.

Item values and properties based on SRD 5.2.1 (EQUIPMENT_REFERENCE.md).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    """Represents an item that can be carried and used.
    
    Attributes:
        name: Display name of the item
        kind: Item category (e.g., 'potion', 'weapon', 'armor')
        value: Gold piece value of the item
        healing: Amount of HP restored if consumable (for potions)
    """
    name: str
    kind: str = ""
    value: int = 0
    healing: int = 0


@dataclass
class Weapon(Item):
    """Represents a weapon that can be equipped.
    
    Attributes:
        dmg_num: Number of damage dice
        dmg_die: Size of damage dice (d4, d6, d8, etc.)
        dmg_bonus: Flat damage bonus
        attack_range: 1 for melee, >1 for ranged
        proficiency_type: Class/group that can use this ('Simple Melee', 'Simple Ranged', 'Martial Melee', 'Martial Ranged')
        weight_lbs: Weight in pounds
    """
    dmg_num: int = 1
    dmg_die: int = 4
    dmg_bonus: int = 0
    attack_range: int = 1
    proficiency_type: str = "Simple Melee"
    weight_lbs: int = 1
    
    def __post_init__(self):
        self.kind = "weapon"


@dataclass
class Armor(Item):
    """Represents armor that can be equipped.
    
    Attributes:
        ac_base: Base AC value
        ac_bonus_dex: Whether DEX bonus applies (True=yes, False=no, 'half'=half DEX)
        max_dex: Maximum DEX bonus that applies (None = no limit)
        proficiency_type: Class/group that can use this ('Light', 'Medium', 'Heavy')
        weight_lbs: Weight in pounds
    """
    ac_base: int = 10
    ac_bonus_dex: bool = True
    max_dex: Optional[int] = None
    proficiency_type: str = "Light"
    weight_lbs: int = 5
    
    def __post_init__(self):
        self.kind = "armor"


# ============================================================================
# WEAPONS (SRD 5e - Player's Handbook)
# ============================================================================

def create_dagger():
    """1d4 piercing, finesse, light. 2 gp."""
    return Weapon(
        name="Dagger",
        dmg_num=1, dmg_die=4, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Simple Melee",
        value=2,
        weight_lbs=1
    )

def create_shortsword():
    """1d6 piercing, finesse, light. 10 gp."""
    return Weapon(
        name="Shortsword",
        dmg_num=1, dmg_die=6, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Martial Melee",
        value=10,
        weight_lbs=2
    )

def create_longsword():
    """1d8 slashing, versatile (1d10 if two-handed). 15 gp."""
    return Weapon(
        name="Longsword",
        dmg_num=1, dmg_die=8, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Martial Melee",
        value=15,
        weight_lbs=3
    )

def create_rapier():
    """1d8 piercing, finesse. 25 gp."""
    return Weapon(
        name="Rapier",
        dmg_num=1, dmg_die=8, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Martial Melee",
        value=25,
        weight_lbs=2
    )

def create_greataxe():
    """1d12 slashing, heavy. 30 gp."""
    return Weapon(
        name="Greataxe",
        dmg_num=1, dmg_die=12, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Martial Melee",
        value=30,
        weight_lbs=7
    )

def create_handaxe():
    """1d6 slashing, light, thrown (20/60). 5 gp."""
    return Weapon(
        name="Handaxe",
        dmg_num=1, dmg_die=6, dmg_bonus=0,
        attack_range=1,
        proficiency_type="Simple Melee",
        value=5,
        weight_lbs=2
    )

def create_bow():
    """1d8 piercing, ranged (80/320), requires ammunition. 25 gp."""
    return Weapon(
        name="Longbow",
        dmg_num=1, dmg_die=8, dmg_bonus=0,
        attack_range=8,  # 80 feet = 8 cells in grid
        proficiency_type="Simple Ranged",
        value=25,
        weight_lbs=2
    )

def create_crossbow():
    """1d8 piercing, ranged (100/400), requires ammunition. 25 gp."""
    return Weapon(
        name="Light Crossbow",
        dmg_num=1, dmg_die=8, dmg_bonus=0,
        attack_range=10,  # 100 feet = 10 cells in grid
        proficiency_type="Simple Ranged",
        value=25,
        weight_lbs=5
    )

# ============================================================================
# ARMOR (SRD 5e)
# ============================================================================

def create_leather_armor():
    """AC 11 + DEX. Lightweight, flexible. 5 gp."""
    return Armor(
        name="Leather Armor",
        ac_base=11,
        ac_bonus_dex=True,
        max_dex=None,
        proficiency_type="Light",
        value=5,
        weight_lbs=10
    )

def create_studded_leather():
    """AC 12 + DEX. Reinforced with metal studs. 45 gp."""
    return Armor(
        name="Studded Leather",
        ac_base=12,
        ac_bonus_dex=True,
        max_dex=None,
        proficiency_type="Light",
        value=45,
        weight_lbs=13
    )

def create_chain_mail():
    """AC 16 (disadvantage on stealth rolls). 75 gp."""
    return Armor(
        name="Chain Mail",
        ac_base=16,
        ac_bonus_dex=False,  # No DEX bonus
        max_dex=0,
        proficiency_type="Heavy",
        value=75,
        weight_lbs=55
    )

def create_plate_armor():
    """AC 18 (disadvantage on stealth). 1500 gp."""
    return Armor(
        name="Plate Armor",
        ac_base=18,
        ac_bonus_dex=False,
        max_dex=0,
        proficiency_type="Heavy",
        value=1500,
        weight_lbs=65
    )

def create_half_plate():
    """AC 15 + DEX (max 2). 750 gp."""
    return Armor(
        name="Half Plate",
        ac_base=15,
        ac_bonus_dex=True,
        max_dex=2,
        proficiency_type="Medium",
        value=750,
        weight_lbs=40
    )

def create_scale_mail():
    """AC 14 + DEX (max 2). 50 gp."""
    return Armor(
        name="Scale Mail",
        ac_base=14,
        ac_bonus_dex=True,
        max_dex=2,
        proficiency_type="Medium",
        value=50,
        weight_lbs=45
    )

# ============================================================================
# CONSUMABLES
# ============================================================================

def create_potion_of_healing():
    """Create a Potion of Healing based on SRD 5.2.1.
    
    From EQUIPMENT_REFERENCE.md:
    - Restores 2d4+2 HP (average 7, range 4-10)
    - Cost: 50 GP
    - Used as Bonus Action
    
    Returns:
        Item configured as Potion of Healing.
    """
    return Item(
        name="Potion of Healing",
        kind="potion",
        value=50,
        healing=7  # Using average of 2d4+2 for consistency
    )


# ============================================================================
# ITEM CATALOGS
# ============================================================================

WEAPONS = {
    "Dagger": create_dagger(),
    "Shortsword": create_shortsword(),
    "Longsword": create_longsword(),
    "Rapier": create_rapier(),
    "Greataxe": create_greataxe(),
    "Handaxe": create_handaxe(),
    "Longbow": create_bow(),
    "Light Crossbow": create_crossbow(),
}

ARMOR = {
    "Leather Armor": create_leather_armor(),
    "Studded Leather": create_studded_leather(),
    "Scale Mail": create_scale_mail(),
    "Half Plate": create_half_plate(),
    "Chain Mail": create_chain_mail(),
    "Plate Armor": create_plate_armor(),
}

CONSUMABLES = {
    "Potion of Healing": create_potion_of_healing(),
}

ALL_ITEMS = {**WEAPONS, **ARMOR, **CONSUMABLES}
