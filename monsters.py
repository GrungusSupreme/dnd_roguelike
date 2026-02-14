"""Monster factory: create varied enemy types with simple behaviors.

Monster stats based on SRD 5.2.1 reference (MONSTERS_REFERENCE.md).
See goblin stat blocks for baseline values.
"""
from character import Character


def make_enemy(wave: int, index: int, bounty: int = 1):
    """Return a Character configured as a monster. Behavior cycles by index:
    0 -> warrior (melee), 1 -> archer (ranged), 2 -> boss (stronger).
    
    Based on SRD 5.2.1 Goblin stat blocks:
    - Goblin Archer: AC 12, HP 7 (2d6), +4 to hit, 1d4+2 damage, CR 1/8
    - Goblin Warrior: AC 15, HP 10 (3d6), +4 to hit, 1d6+2 damage, CR 1/4
    - Goblin Boss: AC 17, HP 21 (6d6), +4 to hit, 1d6+2 damage, CR 1
    
    Wave scaling adds +2 HP and +1 to attack per wave.
    """
    base_name = f"Goblin {wave}-{index+1}"
    wave_scaling_hp = (wave - 1) * 2
    wave_scaling_attack = (wave - 1) // 2

    typ = index % 3
    if typ == 0:
        # Warrior: AC 15, HP 10 base, +4 attack, 1d6+2 damage
        return Character(
            base_name + " Warrior",
            hp=10 + wave_scaling_hp,
            ac=15,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            bounty=bounty,
            behavior="melee"
        )
    if typ == 1:
        # Archer: AC 12, HP 7 base, +4 attack, 1d4+2 damage
        return Character(
            base_name + " Archer",
            hp=7 + wave_scaling_hp,
            ac=12,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=4,
            dmg_bonus=2,
            bounty=bounty,
            behavior="ranged",
            attack_range=3,
        )
    # Boss: AC 17, HP 21 base, +4 attack, 1d6+2 damage, can heal allies
    return Character(
        base_name + " Boss",
        hp=21 + wave_scaling_hp,
        ac=17,
        attack_bonus=4 + wave_scaling_attack,
        dmg_num=1,
        dmg_die=6,
        dmg_bonus=2,
        potions=1,
        bounty=bounty * 2,
        behavior="healer",
        attack_range=1,
    )
