"""Monster factory: create varied enemy types with simple behaviors.

Monster stats based on SRD 5.2.1 reference (MONSTERS_REFERENCE.md).
See goblin stat blocks for baseline values.
"""
from character import Character


def _make_goblin_variant(base_name: str, wave: int, wave_scaling_hp: int, wave_scaling_attack: int, bounty: int, index: int):
    """Legacy goblin variants used as fallback/early-wave baseline."""
    typ = index % 3
    if typ == 0:
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


def make_enemy(wave: int, index: int, bounty: int = 1, archetype: str | None = None):
    """Return a Character configured as a monster.

    Supports mixed archetypes:
    - Goblin Warrior/Archer/Boss
    - Orc Brute
    - Skeleton Archer
    - Troll Brute (regenerates)
    - Goblin Mage
    
    Based on SRD 5.2.1 Goblin stat blocks:
    - Goblin Archer: AC 12, HP 7 (2d6), +4 to hit, 1d4+2 damage, CR 1/8
    - Goblin Warrior: AC 15, HP 10 (3d6), +4 to hit, 1d6+2 damage, CR 1/4
    - Goblin Boss: AC 17, HP 21 (6d6), +4 to hit, 1d6+2 damage, CR 1
    
    Wave scaling adds +2 HP and +1 to attack per wave.
    """
    wave_scaling_hp = (wave - 1) * 2
    wave_scaling_attack = (wave - 1) // 2
    if archetype is None:
        archetype = ["goblin_warrior", "goblin_archer", "goblin_boss"][index % 3]

    archetype = archetype.lower()

    if archetype == "goblin_warrior":
        return Character(
            f"Goblin {wave}-{index+1} Warrior",
            hp=10 + wave_scaling_hp,
            ac=15,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            bounty=bounty,
            behavior="melee",
            attack_range=1,
        )

    if archetype == "goblin_archer":
        return Character(
            f"Goblin {wave}-{index+1} Archer",
            hp=7 + wave_scaling_hp,
            ac=12,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=4,
            dmg_bonus=2,
            bounty=bounty,
            behavior="ranged",
            attack_range=4,
        )

    if archetype == "goblin_boss":
        return Character(
            f"Goblin {wave}-{index+1} Boss",
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

    if archetype == "orc":
        return Character(
            f"Orc {wave}-{index+1}",
            hp=15 + wave_scaling_hp,
            ac=13,
            attack_bonus=5 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=12,
            dmg_bonus=3,
            bounty=bounty + 1,
            behavior="melee",
            attack_range=1,
        )

    if archetype == "skeleton":
        return Character(
            f"Skeleton {wave}-{index+1}",
            hp=9 + wave_scaling_hp,
            ac=13,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            bounty=bounty,
            behavior="ranged",
            attack_range=5,
        )

    if archetype == "troll":
        return Character(
            f"Troll {wave}-{index+1}",
            hp=24 + (wave_scaling_hp * 2),
            ac=14,
            attack_bonus=5 + wave_scaling_attack,
            dmg_num=2,
            dmg_die=6,
            dmg_bonus=2,
            bounty=bounty + 3,
            behavior="regenerator",
            attack_range=1,
        )

    if archetype == "mage":
        return Character(
            f"Goblin Mage {wave}-{index+1}",
            hp=8 + wave_scaling_hp,
            ac=12,
            attack_bonus=5 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=8,
            dmg_bonus=2,
            bounty=bounty + 2,
            behavior="mage",
            attack_range=6,
        )

    return _make_goblin_variant(f"Goblin {wave}-{index+1}", wave, wave_scaling_hp, wave_scaling_attack, bounty, index)
