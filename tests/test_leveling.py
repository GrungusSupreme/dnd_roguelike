import unittest
import character
import dice
import main


class TestLeveling(unittest.TestCase):
    def setUp(self):
        self.player = character.Character("Player", hp=10, ac=10, attack_bonus=5, dmg_num=1, dmg_die=6)
        # bounty 10 -> XP 100 which equals xp_to_next_level for level 1
        self.enemy = character.Character("Champion", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, bounty=10)
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_gain_xp_and_level_up_on_kill(self):
        dice.roll_die = lambda sides=20: 10
        dice.roll_dice = lambda num, sides: 1
        main.run_combat(self.player, [self.enemy], interactive=False)
        # player should have leveled up to level 2
        self.assertGreaterEqual(self.player.level, 2)


if __name__ == "__main__":
    unittest.main()
