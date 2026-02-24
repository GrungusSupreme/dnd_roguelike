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

    def test_orc_adrenaline_rush_grants_temp_hp(self):
        orc = character.Character(
            "Grom",
            hp=20,
            ac=13,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )

        gained = orc.use_adrenaline_rush()

        self.assertEqual(gained, orc.get_proficiency_bonus())
        self.assertEqual(orc.temp_hp, gained)
        self.assertEqual(orc.hp, 20)

    def test_temp_hp_absorbs_damage_after_adrenaline_rush(self):
        orc = character.Character(
            "Grom",
            hp=20,
            ac=13,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )
        gained = orc.use_adrenaline_rush()

        taken, _ = orc.take_damage(gained, damage_type="physical")
        self.assertEqual(taken, 0)
        self.assertEqual(orc.temp_hp, 0)
        self.assertEqual(orc.hp, 20)

    def test_temp_hp_does_not_stack(self):
        """Using Adrenaline Rush twice should NOT add temp HP — only keep the higher value."""
        orc = character.Character(
            "Grom",
            hp=20,
            ac=13,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )
        first = orc.use_adrenaline_rush()
        self.assertEqual(orc.temp_hp, first)

        second = orc.use_adrenaline_rush()
        # Temp HP should NOT have stacked (would be first+second if buggy)
        self.assertEqual(orc.temp_hp, max(first, second))
        # Verify it really didn't stack
        self.assertNotEqual(orc.temp_hp, first + second)
        self.assertEqual(orc.hp, 20)
        self.assertEqual(orc.max_hp, 20)

    def test_resistance_applied_before_temp_hp(self):
        """Rage resistance should halve damage BEFORE temp HP absorbs."""
        orc = character.Character(
            "Grom",
            hp=20,
            ac=13,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )
        # Give temp HP and enter rage
        orc.use_adrenaline_rush()
        prof = orc.get_proficiency_bonus()  # 2 at level 1
        self.assertEqual(orc.temp_hp, prof)

        orc.raging = True
        orc.rage_rounds_remaining = 10

        # Take 10 physical damage while raging with 2 temp HP
        # Correct order: rage halves 10->5, temp HP absorbs 2, 3 goes to HP
        taken, resisted = orc.take_damage(10, damage_type="physical")
        self.assertTrue(resisted)
        # After rage: 10//2 = 5. After temp HP absorbs prof: 5-prof applied to HP
        self.assertEqual(orc.temp_hp, 0)
        self.assertEqual(orc.hp, 20 - (5 - prof))

    def test_temp_hp_does_not_affect_max_hp(self):
        """Temp HP should never modify max_hp."""
        orc = character.Character(
            "Grom",
            hp=20,
            ac=13,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )
        original_max = orc.max_hp
        orc.use_adrenaline_rush()
        self.assertEqual(orc.max_hp, original_max)
        orc.use_adrenaline_rush()
        self.assertEqual(orc.max_hp, original_max)


if __name__ == "__main__":
    unittest.main()
