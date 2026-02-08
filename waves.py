"""Wave spawning and simple scaling logic."""
from character import Character
import monsters


def spawn_wave(wave_number: int, count: int = None):
    """Return a list of enemies for the given wave number.

    Scaling rules (simple):
    - base HP 6, +2 HP per wave (wave 1 -> +0, wave 2 -> +2, ...)
    - base attack bonus 4, +1 every 3 waves
    - default count is wave_number + 1
    """
    if wave_number < 1:
        raise ValueError("wave_number must be >= 1")
    if count is None:
        count = wave_number + 1

    enemies = []
    base_hp = 6
    base_ac = 13
    base_attack = 4
    base_dmg_num = 1
    base_dmg_die = 6

    for i in range(count):
        bounty = 2 + wave_number
        enemies.append(monsters.make_enemy(wave_number, i, bounty=bounty))

    return enemies
