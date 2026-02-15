import unittest
from waves import spawn_wave


class TestWaves(unittest.TestCase):
    def test_spawn_wave_count_default(self):
        enemies = spawn_wave(1)
        self.assertEqual(len(enemies), 2)  # wave 1 -> default count = wave + 1

    def test_spawn_wave_scaling_hp(self):
        e1 = spawn_wave(1, count=1)[0]
        e3 = spawn_wave(3, count=1)[0]
        self.assertLess(e1.hp, e3.hp)

    def test_invalid_wave_number(self):
        with self.assertRaises(ValueError):
            spawn_wave(0)

    def test_wave_three_includes_varied_enemy_types(self):
        enemies = spawn_wave(3, count=6)
        names = [enemy.name for enemy in enemies]
        self.assertTrue(any("Orc" in name for name in names))
        self.assertTrue(any("Skeleton" in name for name in names))
        self.assertTrue(any("Goblin" in name for name in names))

    def test_later_wave_can_spawn_troll_and_mage(self):
        enemies = spawn_wave(6, count=8)
        names = [enemy.name for enemy in enemies]
        self.assertTrue(any("Troll" in name for name in names))
        self.assertTrue(any("Mage" in name for name in names))


if __name__ == "__main__":
    unittest.main()
