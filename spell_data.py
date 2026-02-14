"""Spellcasting data and helpers for combat-focused implementation.

This module intentionally prioritizes level-1 play and combat-relevant spells.
Non-combat spells can be layered in later without changing the runtime API.
"""

from typing import Dict, List


FULL_CASTER_CLASSES = {"Bard", "Cleric", "Druid", "Sorcerer", "Wizard"}
PACT_CASTER_CLASSES = {"Warlock"}


LEVEL1_SPELLCASTING_REQUIREMENTS = {
    "Bard": {"cantrips": 2, "spells": 4, "ability": "CHA"},
    "Cleric": {"cantrips": 3, "spells": 4, "ability": "WIS"},
    "Druid": {"cantrips": 2, "spells": 4, "ability": "WIS"},
    "Sorcerer": {"cantrips": 4, "spells": 2, "ability": "CHA"},
    "Warlock": {"cantrips": 2, "spells": 2, "ability": "CHA"},
    "Wizard": {"cantrips": 3, "spells": 4, "ability": "INT"},
}


CLASS_CANTRIP_OPTIONS = {
    "Bard": ["Vicious Mockery", "Fire Bolt", "Ray of Frost", "Chill Touch"],
    "Cleric": ["Sacred Flame", "Chill Touch", "Poison Spray", "Fire Bolt"],
    "Druid": ["Poison Spray", "Thorn Whip", "Ray of Frost", "Chill Touch"],
    "Sorcerer": ["Fire Bolt", "Ray of Frost", "Chill Touch", "Shocking Grasp", "Poison Spray"],
    "Warlock": ["Eldritch Blast", "Chill Touch", "Poison Spray", "Fire Bolt"],
    "Wizard": ["Fire Bolt", "Ray of Frost", "Chill Touch", "Shocking Grasp", "Poison Spray"],
}


CLASS_LEVEL1_SPELL_OPTIONS = {
    "Bard": ["Dissonant Whispers", "Healing Word", "Cure Wounds", "Thunderwave", "Magic Missile"],
    "Cleric": ["Guiding Bolt", "Cure Wounds", "Healing Word", "Inflict Wounds", "Magic Missile"],
    "Druid": ["Cure Wounds", "Healing Word", "Thunderwave", "Catapult"],
    "Sorcerer": ["Magic Missile", "Burning Hands", "Chromatic Orb", "Witch Bolt", "Thunderwave"],
    "Warlock": ["Arms of Hadar", "Witch Bolt", "Inflict Wounds", "Dissonant Whispers"],
    "Wizard": ["Magic Missile", "Burning Hands", "Chromatic Orb", "Catapult", "Thunderwave", "Witch Bolt"],
}


SPELL_DEFINITIONS: Dict[str, Dict] = {
    "Fire Bolt": {"level": 0, "damage": (1, 10), "damage_type": "fire", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Ray of Frost": {"level": 0, "damage": (1, 8), "damage_type": "cold", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Chill Touch": {"level": 0, "damage": (1, 8), "damage_type": "necrotic", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Sacred Flame": {"level": 0, "damage": (1, 8), "damage_type": "radiant", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Poison Spray": {"level": 0, "damage": (1, 12), "damage_type": "poison", "range": 2, "target": "enemy", "hit_type": "attack"},
    "Vicious Mockery": {"level": 0, "damage": (1, 6), "damage_type": "psychic", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Eldritch Blast": {"level": 0, "damage": (1, 10), "damage_type": "force", "range": 4, "target": "enemy", "hit_type": "attack"},
    "Thorn Whip": {"level": 0, "damage": (1, 6), "damage_type": "piercing", "range": 2, "target": "enemy", "hit_type": "attack"},
    "Shocking Grasp": {"level": 0, "damage": (1, 8), "damage_type": "lightning", "range": 1, "target": "enemy", "hit_type": "attack"},

    "Magic Missile": {"level": 1, "damage": (3, 4), "damage_type": "force", "range": 4, "target": "enemy", "hit_type": "auto", "flat_bonus": 3},
    "Guiding Bolt": {"level": 1, "damage": (4, 6), "damage_type": "radiant", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Inflict Wounds": {"level": 1, "damage": (3, 10), "damage_type": "necrotic", "range": 1, "target": "enemy", "hit_type": "attack"},
    "Burning Hands": {"level": 1, "damage": (3, 6), "damage_type": "fire", "range": 3, "target": "area", "hit_type": "aoe", "aoe": {"shape": "cone", "length": 3}},
    "Chromatic Orb": {"level": 1, "damage": (3, 8), "damage_type": "fire", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Dissonant Whispers": {"level": 1, "damage": (3, 6), "damage_type": "psychic", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Witch Bolt": {"level": 1, "damage": (1, 12), "damage_type": "lightning", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Thunderwave": {"level": 1, "damage": (2, 8), "damage_type": "thunder", "range": 0, "target": "area", "hit_type": "aoe", "aoe": {"shape": "burst_self", "radius": 1}},
    "Arms of Hadar": {"level": 1, "damage": (2, 6), "damage_type": "necrotic", "range": 0, "target": "area", "hit_type": "aoe", "aoe": {"shape": "burst_self", "radius": 1}},
    "Catapult": {"level": 1, "damage": (3, 8), "damage_type": "bludgeoning", "range": 3, "target": "enemy", "hit_type": "attack"},
    "Cure Wounds": {"level": 1, "heal": (1, 8), "range": 1, "target": "self_or_ally", "hit_type": "heal"},
    "Healing Word": {"level": 1, "heal": (1, 4), "range": 3, "target": "self_or_ally", "hit_type": "heal"},
}


def get_spellcasting_requirements(class_name: str) -> Dict[str, int]:
    return dict(LEVEL1_SPELLCASTING_REQUIREMENTS.get(class_name, {"cantrips": 0, "spells": 0, "ability": "INT"}))


def is_spellcaster_class(class_name: str) -> bool:
    return class_name in LEVEL1_SPELLCASTING_REQUIREMENTS


def get_class_spell_options(class_name: str) -> Dict[str, List[str]]:
    return {
        "cantrips": list(CLASS_CANTRIP_OPTIONS.get(class_name, [])),
        "spells": list(CLASS_LEVEL1_SPELL_OPTIONS.get(class_name, [])),
    }


def get_spell_definition(spell_name: str) -> Dict:
    return dict(SPELL_DEFINITIONS.get(spell_name, {}))


def get_spell_slots_max(class_name: str, level: int) -> Dict[int, int]:
    if class_name in FULL_CASTER_CLASSES:
        table = {
            1: {1: 2},
            2: {1: 3},
            3: {1: 4, 2: 2},
            4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2},
        }
        key = min(max(1, level), 5)
        return dict(table[key])
    if class_name in PACT_CASTER_CLASSES:
        table = {
            1: {1: 1},
            2: {1: 2},
            3: {2: 2},
            4: {2: 2},
            5: {3: 2},
        }
        key = min(max(1, level), 5)
        return dict(table[key])
    return {}
