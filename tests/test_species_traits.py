import unittest
import character
import dice


class TestSpeciesTraits(unittest.TestCase):
    def setUp(self):
        self._orig_roll_dice = dice.roll_dice
        self._orig_roll_die = dice.roll_die

    def tearDown(self):
        dice.roll_dice = self._orig_roll_dice
        dice.roll_die = self._orig_roll_die

    def test_dragonborn_initializes_resistance_darkvision_and_breath(self):
        hero = character.Character(
            "Drake",
            hp=20,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Dragonborn",
            species_traits={"Draconic Ancestry": "Red (Fire)"},
        )

        self.assertIn("fire", hero.damage_resistances)
        self.assertEqual(hero.darkvision_range, 60)
        self.assertEqual(hero.breath_weapon_damage_type, "fire")
        self.assertEqual(hero.breath_weapon_uses_remaining, 2)

    def test_take_damage_applies_species_resistance(self):
        hero = character.Character(
            "Drake",
            hp=20,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Dragonborn",
            species_traits={"Draconic Ancestry": "Red (Fire)"},
        )

        taken, resisted = hero.take_damage(10, damage_type="fire")
        self.assertTrue(resisted)
        self.assertEqual(taken, 5)
        self.assertEqual(hero.hp, 15)

    def test_breath_weapon_consumes_use_and_deals_damage(self):
        dice.roll_dice = lambda num, sides: 8
        hero = character.Character(
            "Drake",
            hp=20,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Dragonborn",
            species_traits={"Draconic Ancestry": "Blue (Lightning)"},
        )
        target = character.Character("Goblin", hp=12, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)

        hero.use_breath_weapon(target)

        self.assertEqual(target.hp, 4)
        self.assertEqual(hero.breath_weapon_uses_remaining, 1)

    def test_tiefling_has_fire_resistance(self):
        hero = character.Character(
            "Ash",
            hp=20,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Tiefling",
            species_traits={"Fiendish Legacy": "Infernal"},
        )

        self.assertIn("fire", hero.damage_resistances)
        taken, resisted = hero.take_damage(9, damage_type="fire")
        self.assertTrue(resisted)
        self.assertEqual(taken, 4)
        self.assertEqual(hero.hp, 16)

    def test_lineage_magic_initializes_for_elf(self):
        hero = character.Character(
            "Elara",
            hp=18,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            species="Elf",
            species_traits={"Elven Lineage": "High Elf"},
        )

        self.assertTrue(hero.has_species_magic())
        self.assertEqual(hero.get_species_magic_label(), "High Elf Cantrip")
        self.assertEqual(hero.get_species_magic_range(), 3)

    def test_lineage_magic_can_hit_target(self):
        hero = character.Character(
            "Nyx",
            hp=18,
            ac=12,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=6,
            species="Tiefling",
            species_traits={"Fiendish Legacy": "Chthonic"},
        )
        target = character.Character("Bandit", hp=14, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)

        seq = iter([15])
        dice.roll_die = lambda sides=20: next(seq)
        dice.roll_dice = lambda num, sides: 6

        hero.use_species_magic(target)

        self.assertEqual(target.hp, 8)

    def test_gnome_cunning_has_advantage_on_mental_saves(self):
        gnome = character.Character(
            "Pip",
            hp=18,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            species="Gnome",
            species_traits={"Gnomish Lineage": "Forest Gnome"},
            ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10},
        )
        seq = iter([2, 15])
        dice.roll_die = lambda sides=20: next(seq)

        success, total = gnome.roll_saving_throw("WIS", dc=12)
        self.assertTrue(success)
        self.assertEqual(total, 15)

    def test_goliath_fire_ancestry_uses_are_pb_limited(self):
        goliath = character.Character(
            "Tor",
            hp=24,
            ac=13,
            attack_bonus=6,
            dmg_num=1,
            dmg_die=8,
            species="Goliath",
            species_traits={"Giant Ancestry": "Fire"},
        )
        target = character.Character("Dummy", hp=200, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4)

        dice.roll_die = lambda sides=20: 18
        dice.roll_dice = lambda num, sides: 5

        uses = goliath.giant_ancestry_uses_remaining
        self.assertEqual(uses, goliath.get_proficiency_bonus())
        for _ in range(uses):
            goliath.attack(target)
            # Fire's Burn is an optional on-hit activation
            goliath.activate_on_hit_feature("goliath_fire_burn", target=target)
        self.assertEqual(goliath.giant_ancestry_uses_remaining, 0)
        # Verify no more uses available
        result = goliath.activate_on_hit_feature("goliath_fire_burn", target=target)
        self.assertIn("No uses remaining", result)

    def test_halfling_lucky_rerolls_natural_one(self):
        halfling = character.Character(
            "Nim",
            hp=16,
            ac=12,
            attack_bonus=3,
            dmg_num=1,
            dmg_die=6,
            species="Halfling",
        )
        seq = iter([1, 14])
        dice.roll_die = lambda sides=20: next(seq)
        self.assertEqual(halfling.roll_d20(), 14)

    def test_orc_relentless_endurance_triggers_once(self):
        orc = character.Character(
            "Grom",
            hp=12,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=8,
            species="Orc",
        )

        taken, _ = orc.take_damage(20, damage_type="physical")
        self.assertEqual(taken, 20)
        self.assertEqual(orc.hp, 1)
        self.assertFalse(orc.relentless_endurance_available)

        orc.take_damage(2, damage_type="physical")
        self.assertLessEqual(orc.hp, 0)


if __name__ == "__main__":
    unittest.main()
