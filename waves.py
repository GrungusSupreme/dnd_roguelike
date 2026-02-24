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

    if wave_number == 1:
        archetypes = ["goblin_warrior", "goblin_archer", "goblin_boss"]
    elif wave_number == 2:
        archetypes = ["goblin_warrior", "goblin_archer", "orc", "skeleton"]
    else:
        archetypes = [
            "goblin_warrior",
            "goblin_archer",
            "orc",
            "skeleton",
            "mage",
            "troll",
            "goblin_boss",
            "sneaky",
        ]

    for i in range(count):
        bounty = 2 + wave_number
        archetype = archetypes[i % len(archetypes)]
        enemies.append(monsters.make_enemy(wave_number, i, bounty=bounty, archetype=archetype))

    return enemies
