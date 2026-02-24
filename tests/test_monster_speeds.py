import unittest

from monsters import make_enemy


class TestMonsterSpeeds(unittest.TestCase):
    def test_all_archetypes_have_explicit_30ft_speed(self):
        archetypes = [
            "goblin_warrior",
            "goblin_archer",
            "goblin_boss",
            "orc",
            "skeleton",
            "troll",
            "mage",
        ]
        for idx, archetype in enumerate(archetypes):
            enemy = make_enemy(1, idx, archetype=archetype)
            self.assertEqual(enemy.speed_ft, 30, f"{archetype} speed_ft should be 30")


if __name__ == "__main__":
    unittest.main()
