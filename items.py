"""Item system for D&D roguelike.

Item values and properties based on SRD 5.2.1 (EQUIPMENT_REFERENCE.md).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    """Represents an item that can be carried and used."""

    name: str
    kind: str = ""
    value: float = 0.0
    healing: int = 0


@dataclass
class Weapon(Item):
    """Represents a weapon that can be equipped."""

    dmg_num: int = 1
    dmg_die: int = 4
    dmg_bonus: int = 0
    damage_type: str = "physical"
    attack_range: int = 1
    proficiency_type: str = "Simple Melee"
    weight_lbs: float = 1.0
    finesse: bool = False
    properties: tuple[str, ...] = ()
    mastery: str = ""
    versatile_dmg_die: Optional[int] = None
    range_normal_ft: int = 5
    range_long_ft: int = 5

    def __post_init__(self):
        self.kind = "weapon"

    def has_property(self, prop_name: str) -> bool:
        needle = (prop_name or "").strip().lower()
        return any(str(prop).strip().lower() == needle for prop in self.properties)


@dataclass
class Armor(Item):
    """Represents armor that can be equipped."""

    ac_base: int = 10
    ac_bonus_dex: bool = True
    max_dex: Optional[int] = None
    proficiency_type: str = "Light"
    weight_lbs: float = 5.0
    stealth_disadvantage: bool = False
    strength_requirement: Optional[int] = None

    def __post_init__(self):
        self.kind = "armor"


def _make_weapon(
    *,
    name: str,
    dmg_num: int,
    dmg_die: int,
    damage_type: str,
    proficiency_type: str,
    value: float,
    weight_lbs: float,
    mastery: str,
    properties: tuple[str, ...] = (),
    finesse: bool = False,
    attack_range: Optional[int] = None,
    range_normal_ft: Optional[int] = None,
    range_long_ft: Optional[int] = None,
    versatile_dmg_die: Optional[int] = None,
) -> Weapon:
    if range_normal_ft is None:
        range_normal_ft = 10 if ("Reach" in properties) else 5
    if range_long_ft is None:
        range_long_ft = range_normal_ft
    if attack_range is None:
        attack_range = max(1, int(range_normal_ft // 10))
    return Weapon(
        name=name,
        dmg_num=dmg_num,
        dmg_die=dmg_die,
        dmg_bonus=0,
        damage_type=damage_type,
        attack_range=attack_range,
        proficiency_type=proficiency_type,
        weight_lbs=weight_lbs,
        finesse=finesse,
        properties=properties,
        mastery=mastery,
        versatile_dmg_die=versatile_dmg_die,
        range_normal_ft=range_normal_ft,
        range_long_ft=range_long_ft,
        value=value,
    )


def _make_armor(
    *,
    name: str,
    ac_base: int,
    ac_bonus_dex: bool,
    max_dex: Optional[int],
    proficiency_type: str,
    value: float,
    weight_lbs: float,
    stealth_disadvantage: bool = False,
    strength_requirement: Optional[int] = None,
) -> Armor:
    return Armor(
        name=name,
        ac_base=ac_base,
        ac_bonus_dex=ac_bonus_dex,
        max_dex=max_dex,
        proficiency_type=proficiency_type,
        value=value,
        weight_lbs=weight_lbs,
        stealth_disadvantage=stealth_disadvantage,
        strength_requirement=strength_requirement,
    )


WEAPONS = {
    # Simple Melee
    "Club": _make_weapon(name="Club", dmg_num=1, dmg_die=4, damage_type="bludgeoning", proficiency_type="Simple Melee", value=0.1, weight_lbs=2, mastery="Slow", properties=("Light",)),
    "Dagger": _make_weapon(name="Dagger", dmg_num=1, dmg_die=4, damage_type="piercing", proficiency_type="Simple Melee", value=2, weight_lbs=1, mastery="Nick", properties=("Finesse", "Light", "Thrown"), finesse=True, range_normal_ft=20, range_long_ft=60, attack_range=2),
    "Greatclub": _make_weapon(name="Greatclub", dmg_num=1, dmg_die=8, damage_type="bludgeoning", proficiency_type="Simple Melee", value=0.2, weight_lbs=10, mastery="Push", properties=("Two-Handed",)),
    "Handaxe": _make_weapon(name="Handaxe", dmg_num=1, dmg_die=6, damage_type="slashing", proficiency_type="Simple Melee", value=5, weight_lbs=2, mastery="Vex", properties=("Light", "Thrown"), range_normal_ft=20, range_long_ft=60, attack_range=2),
    "Javelin": _make_weapon(name="Javelin", dmg_num=1, dmg_die=6, damage_type="piercing", proficiency_type="Simple Melee", value=0.5, weight_lbs=2, mastery="Slow", properties=("Thrown",), range_normal_ft=30, range_long_ft=120, attack_range=3),
    "Light Hammer": _make_weapon(name="Light Hammer", dmg_num=1, dmg_die=4, damage_type="bludgeoning", proficiency_type="Simple Melee", value=2, weight_lbs=2, mastery="Nick", properties=("Light", "Thrown"), range_normal_ft=20, range_long_ft=60, attack_range=2),
    "Mace": _make_weapon(name="Mace", dmg_num=1, dmg_die=6, damage_type="bludgeoning", proficiency_type="Simple Melee", value=5, weight_lbs=4, mastery="Sap"),
    "Quarterstaff": _make_weapon(name="Quarterstaff", dmg_num=1, dmg_die=6, damage_type="bludgeoning", proficiency_type="Simple Melee", value=0.2, weight_lbs=4, mastery="Topple", properties=("Versatile",), versatile_dmg_die=8),
    "Sickle": _make_weapon(name="Sickle", dmg_num=1, dmg_die=4, damage_type="slashing", proficiency_type="Simple Melee", value=1, weight_lbs=2, mastery="Nick", properties=("Light",)),
    "Spear": _make_weapon(name="Spear", dmg_num=1, dmg_die=6, damage_type="piercing", proficiency_type="Simple Melee", value=1, weight_lbs=3, mastery="Sap", properties=("Thrown", "Versatile"), versatile_dmg_die=8, range_normal_ft=20, range_long_ft=60, attack_range=2),
    # Simple Ranged
    "Dart": _make_weapon(name="Dart", dmg_num=1, dmg_die=4, damage_type="piercing", proficiency_type="Simple Ranged", value=0.05, weight_lbs=0.25, mastery="Vex", properties=("Finesse", "Thrown"), finesse=True, range_normal_ft=20, range_long_ft=60, attack_range=2),
    "Light Crossbow": _make_weapon(name="Light Crossbow", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Simple Ranged", value=25, weight_lbs=5, mastery="Slow", properties=("Ammunition", "Loading", "Two-Handed"), range_normal_ft=80, range_long_ft=320, attack_range=8),
    "Shortbow": _make_weapon(name="Shortbow", dmg_num=1, dmg_die=6, damage_type="piercing", proficiency_type="Simple Ranged", value=25, weight_lbs=2, mastery="Vex", properties=("Ammunition", "Two-Handed"), range_normal_ft=80, range_long_ft=320, attack_range=8),
    "Sling": _make_weapon(name="Sling", dmg_num=1, dmg_die=4, damage_type="bludgeoning", proficiency_type="Simple Ranged", value=0.1, weight_lbs=0, mastery="Slow", properties=("Ammunition",), range_normal_ft=30, range_long_ft=120, attack_range=3),
    # Martial Melee
    "Battleaxe": _make_weapon(name="Battleaxe", dmg_num=1, dmg_die=8, damage_type="slashing", proficiency_type="Martial Melee", value=10, weight_lbs=4, mastery="Topple", properties=("Versatile",), versatile_dmg_die=10),
    "Flail": _make_weapon(name="Flail", dmg_num=1, dmg_die=8, damage_type="bludgeoning", proficiency_type="Martial Melee", value=10, weight_lbs=2, mastery="Sap"),
    "Glaive": _make_weapon(name="Glaive", dmg_num=1, dmg_die=10, damage_type="slashing", proficiency_type="Martial Melee", value=20, weight_lbs=6, mastery="Graze", properties=("Heavy", "Reach", "Two-Handed"), range_normal_ft=10, attack_range=2),
    "Greataxe": _make_weapon(name="Greataxe", dmg_num=1, dmg_die=12, damage_type="slashing", proficiency_type="Martial Melee", value=30, weight_lbs=7, mastery="Cleave", properties=("Heavy", "Two-Handed")),
    "Greatsword": _make_weapon(name="Greatsword", dmg_num=2, dmg_die=6, damage_type="slashing", proficiency_type="Martial Melee", value=50, weight_lbs=6, mastery="Graze", properties=("Heavy", "Two-Handed")),
    "Halberd": _make_weapon(name="Halberd", dmg_num=1, dmg_die=10, damage_type="slashing", proficiency_type="Martial Melee", value=20, weight_lbs=6, mastery="Cleave", properties=("Heavy", "Reach", "Two-Handed"), range_normal_ft=10, attack_range=2),
    "Lance": _make_weapon(name="Lance", dmg_num=1, dmg_die=10, damage_type="piercing", proficiency_type="Martial Melee", value=10, weight_lbs=6, mastery="Topple", properties=("Heavy", "Reach", "Two-Handed"), range_normal_ft=10, attack_range=2),
    "Longsword": _make_weapon(name="Longsword", dmg_num=1, dmg_die=8, damage_type="slashing", proficiency_type="Martial Melee", value=15, weight_lbs=3, mastery="Sap", properties=("Versatile",), versatile_dmg_die=10),
    "Maul": _make_weapon(name="Maul", dmg_num=2, dmg_die=6, damage_type="bludgeoning", proficiency_type="Martial Melee", value=10, weight_lbs=10, mastery="Topple", properties=("Heavy", "Two-Handed")),
    "Morningstar": _make_weapon(name="Morningstar", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Martial Melee", value=15, weight_lbs=4, mastery="Sap"),
    "Pike": _make_weapon(name="Pike", dmg_num=1, dmg_die=10, damage_type="piercing", proficiency_type="Martial Melee", value=5, weight_lbs=18, mastery="Push", properties=("Heavy", "Reach", "Two-Handed"), range_normal_ft=10, attack_range=2),
    "Rapier": _make_weapon(name="Rapier", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Martial Melee", value=25, weight_lbs=2, mastery="Vex", properties=("Finesse",), finesse=True),
    "Scimitar": _make_weapon(name="Scimitar", dmg_num=1, dmg_die=6, damage_type="slashing", proficiency_type="Martial Melee", value=25, weight_lbs=3, mastery="Nick", properties=("Finesse", "Light"), finesse=True),
    "Shortsword": _make_weapon(name="Shortsword", dmg_num=1, dmg_die=6, damage_type="piercing", proficiency_type="Martial Melee", value=10, weight_lbs=2, mastery="Vex", properties=("Finesse", "Light"), finesse=True),
    "Trident": _make_weapon(name="Trident", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Martial Melee", value=5, weight_lbs=4, mastery="Topple", properties=("Thrown", "Versatile"), versatile_dmg_die=10, range_normal_ft=20, range_long_ft=60, attack_range=2),
    "Warhammer": _make_weapon(name="Warhammer", dmg_num=1, dmg_die=8, damage_type="bludgeoning", proficiency_type="Martial Melee", value=15, weight_lbs=5, mastery="Push", properties=("Versatile",), versatile_dmg_die=10),
    "War Pick": _make_weapon(name="War Pick", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Martial Melee", value=5, weight_lbs=2, mastery="Sap", properties=("Versatile",), versatile_dmg_die=10),
    "Whip": _make_weapon(name="Whip", dmg_num=1, dmg_die=4, damage_type="slashing", proficiency_type="Martial Melee", value=2, weight_lbs=3, mastery="Slow", properties=("Finesse", "Reach"), finesse=True, range_normal_ft=10, attack_range=2),
    # Martial Ranged
    "Blowgun": _make_weapon(name="Blowgun", dmg_num=1, dmg_die=1, damage_type="piercing", proficiency_type="Martial Ranged", value=10, weight_lbs=1, mastery="Vex", properties=("Ammunition", "Loading"), range_normal_ft=25, range_long_ft=100, attack_range=2),
    "Hand Crossbow": _make_weapon(name="Hand Crossbow", dmg_num=1, dmg_die=6, damage_type="piercing", proficiency_type="Martial Ranged", value=75, weight_lbs=3, mastery="Vex", properties=("Ammunition", "Light", "Loading"), range_normal_ft=30, range_long_ft=120, attack_range=3),
    "Heavy Crossbow": _make_weapon(name="Heavy Crossbow", dmg_num=1, dmg_die=10, damage_type="piercing", proficiency_type="Martial Ranged", value=50, weight_lbs=18, mastery="Push", properties=("Ammunition", "Heavy", "Loading", "Two-Handed"), range_normal_ft=100, range_long_ft=400, attack_range=10),
    "Longbow": _make_weapon(name="Longbow", dmg_num=1, dmg_die=8, damage_type="piercing", proficiency_type="Martial Ranged", value=50, weight_lbs=2, mastery="Slow", properties=("Ammunition", "Heavy", "Two-Handed"), range_normal_ft=150, range_long_ft=600, attack_range=15),
    "Musket": _make_weapon(name="Musket", dmg_num=1, dmg_die=12, damage_type="piercing", proficiency_type="Martial Ranged", value=500, weight_lbs=10, mastery="Slow", properties=("Ammunition", "Loading", "Two-Handed"), range_normal_ft=40, range_long_ft=120, attack_range=4),
    "Pistol": _make_weapon(name="Pistol", dmg_num=1, dmg_die=10, damage_type="piercing", proficiency_type="Martial Ranged", value=250, weight_lbs=3, mastery="Vex", properties=("Ammunition", "Loading"), range_normal_ft=30, range_long_ft=90, attack_range=3),
}

ARMOR = {
    # Light
    "Padded Armor": _make_armor(name="Padded Armor", ac_base=11, ac_bonus_dex=True, max_dex=None, proficiency_type="Light", value=5, weight_lbs=8, stealth_disadvantage=True),
    "Leather Armor": _make_armor(name="Leather Armor", ac_base=11, ac_bonus_dex=True, max_dex=None, proficiency_type="Light", value=10, weight_lbs=10),
    "Studded Leather Armor": _make_armor(name="Studded Leather Armor", ac_base=12, ac_bonus_dex=True, max_dex=None, proficiency_type="Light", value=45, weight_lbs=13),
    # Medium
    "Hide Armor": _make_armor(name="Hide Armor", ac_base=12, ac_bonus_dex=True, max_dex=2, proficiency_type="Medium", value=10, weight_lbs=12),
    "Chain Shirt": _make_armor(name="Chain Shirt", ac_base=13, ac_bonus_dex=True, max_dex=2, proficiency_type="Medium", value=50, weight_lbs=20),
    "Scale Mail": _make_armor(name="Scale Mail", ac_base=14, ac_bonus_dex=True, max_dex=2, proficiency_type="Medium", value=50, weight_lbs=45, stealth_disadvantage=True),
    "Breastplate": _make_armor(name="Breastplate", ac_base=14, ac_bonus_dex=True, max_dex=2, proficiency_type="Medium", value=400, weight_lbs=20),
    "Half Plate Armor": _make_armor(name="Half Plate Armor", ac_base=15, ac_bonus_dex=True, max_dex=2, proficiency_type="Medium", value=750, weight_lbs=40, stealth_disadvantage=True),
    # Heavy
    "Ring Mail": _make_armor(name="Ring Mail", ac_base=14, ac_bonus_dex=False, max_dex=0, proficiency_type="Heavy", value=30, weight_lbs=40, stealth_disadvantage=True),
    "Chain Mail": _make_armor(name="Chain Mail", ac_base=16, ac_bonus_dex=False, max_dex=0, proficiency_type="Heavy", value=75, weight_lbs=55, stealth_disadvantage=True, strength_requirement=13),
    "Splint Armor": _make_armor(name="Splint Armor", ac_base=17, ac_bonus_dex=False, max_dex=0, proficiency_type="Heavy", value=200, weight_lbs=60, stealth_disadvantage=True, strength_requirement=15),
    "Plate Armor": _make_armor(name="Plate Armor", ac_base=18, ac_bonus_dex=False, max_dex=0, proficiency_type="Heavy", value=1500, weight_lbs=65, stealth_disadvantage=True, strength_requirement=15),
}

# Backward-compatible aliases used by earlier saves/UI labels
ARMOR["Studded Leather"] = ARMOR["Studded Leather Armor"]
ARMOR["Half Plate"] = ARMOR["Half Plate Armor"]


# Backward-compatible factory helpers used by tests and existing code

def create_dagger() -> Weapon:
    return WEAPONS["Dagger"]


def create_shortsword() -> Weapon:
    return WEAPONS["Shortsword"]


def create_longsword() -> Weapon:
    return WEAPONS["Longsword"]


def create_rapier() -> Weapon:
    return WEAPONS["Rapier"]


def create_greataxe() -> Weapon:
    return WEAPONS["Greataxe"]


def create_handaxe() -> Weapon:
    return WEAPONS["Handaxe"]


def create_bow() -> Weapon:
    return WEAPONS["Longbow"]


def create_crossbow() -> Weapon:
    return WEAPONS["Light Crossbow"]


def create_leather_armor() -> Armor:
    return ARMOR["Leather Armor"]


def create_studded_leather() -> Armor:
    return ARMOR["Studded Leather Armor"]


def create_chain_mail() -> Armor:
    return ARMOR["Chain Mail"]


def create_plate_armor() -> Armor:
    return ARMOR["Plate Armor"]


def create_half_plate() -> Armor:
    return ARMOR["Half Plate Armor"]


def create_scale_mail() -> Armor:
    return ARMOR["Scale Mail"]


def create_potion_of_healing() -> Item:
    return Item(
        name="Potion of Healing",
        kind="potion",
        value=50,
        healing=7,
    )


CONSUMABLES = {
    "Potion of Healing": create_potion_of_healing(),
}

ALL_ITEMS = {**WEAPONS, **ARMOR, **CONSUMABLES}
