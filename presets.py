"""Character preset save/load helpers."""
import json
import os
from typing import Any, Dict, List

from character import Character
from class_definitions import generate_level_1_stats, get_default_ability_scores
from character_creation_data import SPECIES_SPEED_FEET

PRESET_FILE = os.path.join(os.path.dirname(__file__), "presets.json")


def load_presets() -> List[Dict[str, Any]]:
    if not os.path.exists(PRESET_FILE):
        return []
    try:
        with open(PRESET_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [entry for entry in data if isinstance(entry, dict)]


def save_preset(preset: Dict[str, Any]) -> None:
    presets = load_presets()
    name = preset.get("name")
    if name:
        presets = [entry for entry in presets if entry.get("name") != name]
    presets.append(preset)
    with open(PRESET_FILE, "w", encoding="utf-8") as handle:
        json.dump(presets, handle, indent=2, sort_keys=True)


def delete_preset(name: str) -> None:
    """Delete a preset by name."""
    presets = load_presets()
    presets = [entry for entry in presets if entry.get("name") != name]
    with open(PRESET_FILE, "w", encoding="utf-8") as handle:
        json.dump(presets, handle, indent=2, sort_keys=True)


def _class_attack_range(class_name: str) -> int:
    class_ranges = {
        "Bard": 2,
        "Druid": 2,
        "Ranger": 3,
        "Rogue": 2,
        "Sorcerer": 3,
        "Warlock": 3,
        "Wizard": 3,
    }
    return class_ranges.get(class_name, 1)


def build_character_from_preset(preset: Dict[str, Any]) -> Character:
    class_name = preset.get("class_name") or "Fighter"
    ability_scores = preset.get("ability_scores") or get_default_ability_scores(class_name)
    stats = generate_level_1_stats(class_name, ability_scores)

    species = preset.get("species")
    species_key = species if isinstance(species, str) else None
    if species_key is None:
        speed_ft = 30
    else:
        speed_ft = SPECIES_SPEED_FEET.get(species_key, 30)

    return Character(
        preset.get("name", "Hero"),
        hp=stats["hp"],
        ac=stats["ac"],
        attack_bonus=stats["attack_bonus"],
        dmg_num=stats["dmg_num"],
        dmg_die=stats["dmg_die"],
        dmg_bonus=stats["dmg_bonus"],
        initiative_bonus=stats["initiative_bonus"],
        class_name=class_name,
        ability_scores=stats["ability_scores"],
        attack_range=_class_attack_range(class_name),
        skill_proficiencies=preset.get("skill_proficiencies", []),
        tool_proficiencies=preset.get("tool_proficiencies", []),
        weapon_masteries=preset.get("weapon_masteries", []),
        species=species,
        species_traits=preset.get("species_traits", {}),
        origin_feats=preset.get("origin_feats", []),
        spells=preset.get("spells", []),
        spell_slots_current={int(k): v for k, v in preset.get("spell_slots_current", {}).items()} if isinstance(preset.get("spell_slots_current"), dict) else None,
        spell_slots_max={int(k): v for k, v in preset.get("spell_slots_max", {}).items()} if isinstance(preset.get("spell_slots_max"), dict) else None,
        speed_ft=speed_ft,
        gold=preset.get("gold", 50),
    )
