"""Interactive character creator for the dnd_roguelike demo.

Provides a small CLI helper `create_character_interactive()` that returns a
`Character` instance configured with a chosen name and class.
"""
from character import Character
from class_definitions import generate_level_1_stats, get_default_ability_scores
from character_creation_data import (
    ABILITY_CODES,
    ALL_SKILLS,
    ORIGIN_FEAT_OPTIONS,
    TOOL_PROFICIENCY_OPTIONS,
)
from spell_data import get_class_spell_options, get_spellcasting_requirements, is_spellcaster_class


def _choose(prompt, options):
    print(prompt)
    for i, (key, desc) in enumerate(options, start=1):
        print(f"  {i}. {desc}")
    while True:
        choice = input("Choose an option number: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
        print("Invalid selection, try again.")


def _choose_multiple(prompt, options, count):
    while True:
        print(prompt)
        for i, option in enumerate(options, start=1):
            print(f"  {i}. {option}")
        raw = input(f"Choose {count} numbers separated by spaces: ").strip()
        if not raw:
            print("Please enter a selection.")
            continue
        parts = [p for p in raw.replace(",", " ").split() if p.isdigit()]
        if len(parts) != count:
            print("Invalid count, try again.")
            continue
        indexes = [int(p) - 1 for p in parts]
        if any(i < 0 or i >= len(options) for i in indexes):
            print("Invalid selection, try again.")
            continue
        if len(set(indexes)) != count:
            print("Selections must be different.")
            continue
        return [options[i] for i in indexes]


def _cost_to_score(score: int) -> int:
    """Return the point-buy cost to reach `score` from base 8.

    Uses the classic 5e-style costs: 8->0, 9->1, 10->2, 11->3, 12->4, 13->5,
    14->7, 15->9. Scores below 8 or above 15 are not supported.
    """
    if score < 8 or score > 15:
        raise ValueError("score must be between 8 and 15")
    costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    return costs[score]


def _point_buy_interactive():
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    scores = {a: 8 for a in abilities}
    pool = 27

    def remaining_cost_for_change(curr, target):
        return _cost_to_score(target) - _cost_to_score(curr)

    print("Starting point-buy: 27 points, scores start at 8, min 8, max 15.")
    while True:
        print(f"Points remaining: {pool}")
        print("Current scores:")
        for a in abilities:
            print(f"  {a}: {scores[a]}")
        choice = input("Enter ability to increase (STR DEX CON INT WIS CHA), 'done' to finish, or 'reset': ").strip().upper()
        if choice == "DONE":
            return scores
        if choice == "RESET":
            scores = {a: 8 for a in abilities}
            pool = 27
            continue
        if choice not in abilities:
            print("Invalid ability code.")
            continue
        curr = scores[choice]
        if curr >= 15:
            print(f"{choice} is already at maximum (15).")
            continue
        try:
            target_raw = input(f"Enter target score for {choice} (current {curr}, max 15): ").strip()
            target = int(target_raw)
        except Exception:
            print("Invalid number.")
            continue
        if target < curr or target > 15 or target < 8:
            print("Target must be between current score and 15.")
            continue
        cost = remaining_cost_for_change(curr, target)
        if cost > pool:
            print(f"Not enough points (need {cost}, have {pool}).")
            continue
        scores[choice] = target
        pool -= cost


def create_character_interactive():
    name = input("Enter your character's name: ").strip()
    if not name:
        name = "Player"

    archetypes = [
        ("Barbarian", "Barbarian - hardy melee bruiser (high HP, heavy damage)."),
        ("Bard", "Bard - versatile support with social flair and spells."),
        ("Cleric", "Cleric - divine caster and healer (starts with potions)."),
        ("Druid", "Druid - nature caster with healing and utility."),
        ("Fighter", "Fighter - well-rounded frontline specialist."),
        ("Monk", "Monk - fast striker with high initiative."),
        ("Paladin", "Paladin - tanky warrior with strong melee."),
        ("Ranger", "Ranger - skilled at ranged combat and tracking."),
        ("Rogue", "Rogue - high precision strikes and high initiative."),
        ("Sorcerer", "Sorcerer - spontaneous caster with arcane power."),
        ("Warlock", "Warlock - pact-bound caster with reliable spells."),
        ("Wizard", "Wizard - classic arcane scholar with powerful spells."),
    ]

    pick = _choose("Choose an archetype:", archetypes)

    starting_potions = {
        "Barbarian": 0,
        "Bard": 1,
        "Cleric": 2,
        "Druid": 2,
        "Fighter": 1,
        "Monk": 0,
        "Paladin": 1,
        "Ranger": 1,
        "Rogue": 0,
        "Sorcerer": 0,
        "Warlock": 0,
        "Wizard": 0,
    }

    class_ranges = {
        "Bard": 2,
        "Druid": 2,
        "Ranger": 3,
        "Rogue": 2,
        "Sorcerer": 3,
        "Warlock": 3,
        "Wizard": 3,
    }

    ability_scores = get_default_ability_scores(pick)
    do_pb = input("Customize ability scores with point-buy? (y/N): ").strip().lower()
    if do_pb == "y":
        ability_scores = _point_buy_interactive()

    print("\nCustom Background Setup")
    chosen_abilities = _choose_multiple(
        "Choose three different ability scores:",
        ABILITY_CODES,
        3,
    )
    asi_mode = _choose(
        "Choose ability bonus mode:",
        [
            ("2_1", "+2 to one, +1 to another"),
            ("1_1_1", "+1 to all three"),
        ],
    )
    if asi_mode == "2_1":
        primary = _choose("Choose which ability gets +2:", [(a, a) for a in chosen_abilities])
        secondary = _choose("Choose which ability gets +1:", [(a, a) for a in chosen_abilities if a != primary])
        ability_scores[primary] = min(20, ability_scores[primary] + 2)
        ability_scores[secondary] = min(20, ability_scores[secondary] + 1)
    else:
        for ability in chosen_abilities:
            ability_scores[ability] = min(20, ability_scores[ability] + 1)

    origin_feat = _choose("Choose an origin feat:", [(f, f) for f in ORIGIN_FEAT_OPTIONS])
    skills = _choose_multiple("Choose two skill proficiencies:", ALL_SKILLS, 2)
    tool = _choose("Choose a tool proficiency:", [(t, t) for t in TOOL_PROFICIENCY_OPTIONS])

    selected_spells = []
    if is_spellcaster_class(pick):
        req = get_spellcasting_requirements(pick)
        options = get_class_spell_options(pick)
        cantrip_count = req.get("cantrips", 0)
        spell_count = req.get("spells", 0)
        if cantrip_count > 0:
            selected_spells.extend(
                _choose_multiple("Choose cantrips:", options.get("cantrips", []), cantrip_count)
            )
        if spell_count > 0:
            selected_spells.extend(
                _choose_multiple("Choose level 1 spells:", options.get("spells", []), spell_count)
            )

    stats = generate_level_1_stats(pick, ability_scores)

    return Character(
        name,
        hp=stats["hp"],
        ac=stats["ac"],
        attack_bonus=stats["attack_bonus"],
        dmg_num=stats["dmg_num"],
        dmg_die=stats["dmg_die"],
        dmg_bonus=stats["dmg_bonus"],
        initiative_bonus=stats["initiative_bonus"],
        potions=starting_potions.get(pick, 0),
        class_name=pick,
        ability_scores=stats["ability_scores"],
        attack_range=class_ranges.get(pick, 1),
        skill_proficiencies=skills,
        tool_proficiencies=[tool],
        origin_feats=[origin_feat],
        spells=selected_spells,
        gold=50,
    )
