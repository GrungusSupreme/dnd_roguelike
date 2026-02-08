"""Monster factory: create varied enemy types with simple behaviors."""
from character import Character


def make_enemy(wave: int, index: int, bounty: int = 1):
    """Return a Character configured as a monster. Behavior cycles by index:
    0 -> melee (standard), 1 -> ranged, 2 -> healer/support.
    """
    base_name = f"Goblin {wave}-{index+1}"
    # scaling
    hp = 6 + (wave - 1) * 2
    ac = 13
    attack_bonus = 4 + (wave - 1) // 3

    typ = index % 3
    if typ == 0:
        # melee
        return Character(base_name, hp=hp, ac=ac, attack_bonus=attack_bonus, dmg_num=1, dmg_die=6, bounty=bounty, behavior="melee")
    if typ == 1:
        # ranged: slightly higher damage die
        return Character(base_name + " (Archer)", hp=hp - 1, ac=ac - 1, attack_bonus=attack_bonus, dmg_num=1, dmg_die=8, bounty=bounty, behavior="ranged")
    # healer/support
    # give them a potion to heal allies
    return Character(base_name + " (Shaman)", hp=hp - 2, ac=ac - 1, attack_bonus=attack_bonus - 1, dmg_num=1, dmg_die=4, potions=1, bounty=bounty, behavior="healer")
