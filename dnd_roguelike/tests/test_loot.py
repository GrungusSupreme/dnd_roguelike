import unittest
import character
import dice
import main


class TestLoot(unittest.TestCase):
    def setUp(self):
        self.player = character.Character("Player", hp=10, ac=10, attack_bonus=5, dmg_num=1, dmg_die=6)
        self.enemy = character.Character("Goblin", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, bounty=3)
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_loot_on_kill(self):
        # Ensure player hits and deals 1 damage to kill the goblin
        dice.roll_die = lambda *a, **k: 10
        dice.roll_dice = lambda num, sides: 1
        survived = main.run_combat(self.player, [self.enemy], interactive=False)
        self.assertTrue(survived)
        self.assertEqual(self.player.gold, 3)


if __name__ == "__main__":
    unittest.main()
