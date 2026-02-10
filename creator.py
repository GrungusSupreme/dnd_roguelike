"""Interactive character creator for the dnd_roguelike demo.

Provides a small CLI helper `create_character_interactive()` that returns a
`Character` instance configured with a chosen name and archetype. The creator
keeps things simple: predefined archetypes (Fighter, Rogue, Healer) with
balanced starting stats.
"""
from character import Character


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


def _apply_scores_to_character(char: Character, scores: dict):
    """Apply ability score modifiers to a `Character` instance in a simple way.

    This keeps the game mechanics light: modifiers influence HP, attack,
    damage, AC, and initiative.
    """
    def mod(score):
        return (score - 10) // 2

    str_mod = mod(scores["STR"])
    dex_mod = mod(scores["DEX"])
    con_mod = mod(scores["CON"])
    int_mod = mod(scores["INT"])
    wis_mod = mod(scores["WIS"])
    cha_mod = mod(scores["CHA"])

    # Apply simple effects
    char.max_hp += con_mod * 2
    char.hp = min(char.max_hp, char.hp + max(0, con_mod * 2))
    char.attack_bonus += max(0, str_mod)
    char.dmg_bonus += max(0, str_mod)
    char.initiative_bonus += dex_mod
    if dex_mod > 0:
        char.ac += dex_mod



def create_character_interactive():
    name = input("Enter your character's name: ").strip()
    if not name:
        name = "Player"

    archetypes = [
        ("artificer", "Artificer — magical inventor and item crafter."),
        ("barbarian", "Barbarian — hardy melee bruiser (high HP, heavy damage)."),
        ("bard", "Bard — versatile support with social flair and spells."),
        ("cleric", "Cleric — divine caster and healer (starts with potions)."),
        ("druid", "Druid — nature caster with healing and utility."),
        ("fighter", "Fighter — well-rounded frontline specialist."),
        ("monk", "Monk — fast striker with high initiative."),
        ("paladin", "Paladin — tanky warrior with strong melee."),
        ("ranger", "Ranger — skilled at ranged combat and tracking."),
        ("rogue", "Rogue — high precision strikes and high initiative."),
        ("sorcerer", "Sorcerer — spontaneous caster with arcane power."),
        ("warlock", "Warlock — pact-bound caster with reliable spells."),
        ("wizard", "Wizard — classic arcane scholar with powerful spells."),
    ]

    pick = _choose("Choose an archetype:", archetypes)

    # base presets for each class
    presets = {
        "artificer": dict(hp=25, ac=14, attack_bonus=4, dmg_num=1, dmg_die=6, dmg_bonus=1, initiative_bonus=1, potions=1, bounty=1),
        "barbarian": dict(hp=36, ac=14, attack_bonus=6, dmg_num=1, dmg_die=12, dmg_bonus=4, initiative_bonus=1, potions=0, bounty=1),
        "bard": dict(hp=26, ac=13, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=2, initiative_bonus=2, potions=1, bounty=1),
        "cleric": dict(hp=28, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=2, initiative_bonus=1, potions=2, bounty=1, behavior="healer"),
        "druid": dict(hp=26, ac=14, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=2, initiative_bonus=1, potions=2, bounty=1, behavior="healer"),
        "fighter": dict(hp=34, ac=16, attack_bonus=6, dmg_num=1, dmg_die=8, dmg_bonus=3, initiative_bonus=1, potions=1, bounty=1),
        "monk": dict(hp=24, ac=15, attack_bonus=6, dmg_num=1, dmg_die=8, dmg_bonus=2, initiative_bonus=3, potions=0, bounty=1),
        "paladin": dict(hp=32, ac=17, attack_bonus=6, dmg_num=1, dmg_die=8, dmg_bonus=4, initiative_bonus=1, potions=1, bounty=1),
        "ranger": dict(hp=28, ac=14, attack_bonus=6, dmg_num=1, dmg_die=10, dmg_bonus=3, initiative_bonus=2, potions=1, bounty=1),
        "rogue": dict(hp=24, ac=13, attack_bonus=7, dmg_num=1, dmg_die=6, dmg_bonus=4, initiative_bonus=3, potions=0, bounty=1),
        "sorcerer": dict(hp=22, ac=12, attack_bonus=4, dmg_num=1, dmg_die=6, dmg_bonus=3, initiative_bonus=2, potions=0, bounty=1),
        "warlock": dict(hp=24, ac=13, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=3, initiative_bonus=2, potions=0, bounty=1),
        "wizard": dict(hp=20, ac=12, attack_bonus=4, dmg_num=1, dmg_die=6, dmg_bonus=2, initiative_bonus=1, potions=0, bounty=1),
    }

    params = presets.get(pick, presets["fighter"])  # fallback
    char = Character(name, **params)

    # Offer point-buy customization
    do_pb = input("Customize ability scores with point-buy? (y/N): ").strip().lower()
    if do_pb == "y":
        scores = _point_buy_interactive()
        _apply_scores_to_character(char, scores)

    return char
