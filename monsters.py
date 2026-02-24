"""Monster factory: create varied enemy types with simple behaviors.

Monster stats based on SRD 5.2.1 reference (MONSTERS_REFERENCE.md).
See goblin stat blocks for baseline values.
"""
from character import Character


def _with_senses(enemy: Character, passive_perception: int, darkvision_range: int = 0) -> Character:
    enemy.passive_perception = passive_perception
    if darkvision_range > 0:
        enemy.darkvision_range = darkvision_range
    return enemy


def _make_goblin_variant(base_name: str, wave: int, wave_scaling_hp: int, wave_scaling_attack: int, bounty: int, index: int):
    """Legacy goblin variants used as fallback/early-wave baseline."""
    typ = index % 3
    if typ == 0:
        return _with_senses(Character(
            base_name + " Warrior",
            hp=10 + wave_scaling_hp,
            ac=15,
            attack_bonus=4 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            bounty=bounty,
            behavior="melee",
            speed_ft=30,
        ), passive_perception=9, darkvision_range=60)
    if typ == 1:
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=9, darkvision_range=60)
    return _with_senses(Character(
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
        speed_ft=30,
    ), passive_perception=10, darkvision_range=60)


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
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=9, darkvision_range=60)

    if archetype == "goblin_archer":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=9, darkvision_range=60)

    if archetype == "goblin_boss":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=10, darkvision_range=60)

    if archetype == "orc":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=10, darkvision_range=60)

    if archetype == "skeleton":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=8, darkvision_range=60)

    if archetype == "troll":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=13, darkvision_range=60)

    if archetype == "mage":
        return _with_senses(Character(
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
            speed_ft=30,
        ), passive_perception=10, darkvision_range=60)

    if archetype == "sneaky":
        enemy = _with_senses(Character(
            f"Goblin Skulk {wave}-{index+1}",
            hp=7 + wave_scaling_hp,
            ac=13,
            attack_bonus=5 + wave_scaling_attack,
            dmg_num=1,
            dmg_die=4,
            dmg_bonus=2,
            bounty=bounty + 1,
            behavior="sneaky",
            attack_range=3,
            speed_ft=30,
        ), passive_perception=12, darkvision_range=60)
        enemy.stealth_bonus = 6 + wave_scaling_attack  # +6 Stealth base, scales
        enemy.sneak_attack_dice = 1 + (wave - 1) // 3  # 1d6 base, +1d6 every 3 waves
        return enemy

    return _make_goblin_variant(f"Goblin {wave}-{index+1}", wave, wave_scaling_hp, wave_scaling_attack, bounty, index)
