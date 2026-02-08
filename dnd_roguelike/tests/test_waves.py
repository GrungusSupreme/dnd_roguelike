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


if __name__ == "__main__":
    unittest.main()
