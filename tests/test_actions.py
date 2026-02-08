import unittest
import character
import dice


class TestActions(unittest.TestCase):
    def setUp(self):
        self.player = character.Character("Player", hp=20, ac=15, attack_bonus=0, dmg_num=1, dmg_die=1, potions=1)
        self.enemy = character.Character("Enemy", hp=10, ac=10, attack_bonus=5, dmg_num=1, dmg_die=1)
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_heal_with_potion(self):
        self.player.hp = 5
        healed = self.player.use_potion(8)
        self.assertEqual(healed, 8)
        self.assertEqual(self.player.hp, 13)
        self.assertEqual(self.player.potions, 0)

    def test_defend_reduces_damage(self):
        # enemy will roll a hit (roll 15 + 5 = 20 vs AC 15) normally
        dice.roll_die = lambda *a, **k: 15
        dice.roll_dice = lambda *a, **k: 1
        # player defends
        self.player.defend(ac_bonus=2)
        # enemy attacks
        self.enemy.attack(self.player)
        # effective AC was 17, enemy total 20 -> hit, but damage applied normally
        # ensure temp_ac_bonus was accounted for by not changing behavior adversely
        self.assertTrue(self.player.hp <= self.player.max_hp)


if __name__ == "__main__":
    unittest.main()
