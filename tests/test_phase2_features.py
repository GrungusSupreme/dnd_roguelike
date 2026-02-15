import unittest

import character
import dice
from main_gui import GameState


class TestPhase2Features(unittest.TestCase):
    def setUp(self):
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_barbarian_unarmored_defense(self):
        barb = character.Character(
            "Barb",
            hp=20,
            ac=10,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=8,
            class_name="Barbarian",
            ability_scores={"STR": 16, "DEX": 14, "CON": 16, "INT": 8, "WIS": 10, "CHA": 10},
        )
        self.assertEqual(barb.get_ac(), 15)

    def test_monk_unarmored_defense(self):
        monk = character.Character(
            "Monk",
            hp=16,
            ac=10,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        self.assertEqual(monk.get_ac(), 15)

    def test_poisoned_reduces_attack_roll(self):
        attacker = character.Character("Attacker", hp=10, ac=10, attack_bonus=5, dmg_num=1, dmg_die=6)
        defender = character.Character(
            "Defender",
            hp=12,
            ac=15,
            attack_bonus=0,
            dmg_num=1,
            dmg_die=4,
            ability_scores={"STR": 10, "DEX": 20, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10},
        )

        dice.roll_die = lambda sides=20: 10
        dice.roll_dice = lambda num, sides: 1

        attacker.attack(defender)
        self.assertEqual(defender.hp, 11)

        defender.hp = 12
        attacker.apply_status_effect("poisoned", rounds=2)
        attacker.attack(defender)
        self.assertEqual(defender.hp, 12)

    def test_action_surge_economy_gain(self):
        fighter = character.Character("Fighter", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8, class_name="Fighter")
        state = GameState(fighter)

        self.assertTrue(state.can_use_action())
        self.assertTrue(state.spend_action())
        self.assertFalse(state.can_use_action())

        state.gain_action(1)
        self.assertTrue(state.can_use_action())
        self.assertTrue(state.spend_action())
        self.assertFalse(state.can_use_action())


if __name__ == "__main__":
    unittest.main()
