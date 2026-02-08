import unittest
import character
import dice
import main


class TestItems(unittest.TestCase):
    def setUp(self):
        self.player = character.Character("Player", hp=10, ac=10, attack_bonus=5, dmg_num=1, dmg_die=6)
        self.enemy = character.Character("Goblin", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, bounty=3)
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_potion_drop_on_kill(self):
        # stub roll: regular rolls return 10 (hits), but 100-sided roll returns 1 (drop)
        def roll_die_stub(sides=20):
            return 1 if sides == 100 else 10

        dice.roll_die = roll_die_stub
        dice.roll_dice = lambda num, sides: 1
        survived = main.run_combat(self.player, [self.enemy], interactive=False)
        self.assertTrue(survived)
        # potion added via add_item increments potions
        self.assertGreaterEqual(self.player.potions, 1)


if __name__ == "__main__":
    unittest.main()
