import unittest
import character
import dice
from spell_data import get_spell_definition


class TestSpells(unittest.TestCase):
    def setUp(self):
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_spellcaster_has_level1_slots(self):
        wizard = character.Character(
            "Merin",
            hp=14,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Magic Missile", "Fire Bolt"],
        )
        self.assertEqual(wizard.spell_slots_max.get(1), 2)
        self.assertEqual(wizard.spell_slots_current.get(1), 2)

    def test_level1_spell_consumes_slot_and_deals_damage(self):
        dice.roll_dice = lambda num, sides: 2  # Magic Missile base die result
        caster = character.Character(
            "Merin",
            hp=14,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Magic Missile"],
        )
        target = character.Character("Goblin", hp=20, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)

        caster.cast_spell("Magic Missile", target=target)

        self.assertEqual(caster.spell_slots_current.get(1), 1)
        self.assertEqual(target.hp, 15)

    def test_cantrip_does_not_consume_slot(self):
        dice.roll_die = lambda sides=20: 15
        dice.roll_dice = lambda num, sides: 5
        caster = character.Character(
            "Merin",
            hp=14,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Fire Bolt"],
        )
        target = character.Character("Goblin", hp=20, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)
        before = caster.spell_slots_current.get(1)

        caster.cast_spell("Fire Bolt", target=target)

        self.assertEqual(caster.spell_slots_current.get(1), before)
        self.assertLess(target.hp, 20)

    def test_healing_word_restores_hp(self):
        dice.roll_dice = lambda num, sides: 4
        cleric = character.Character(
            "Ari",
            hp=20,
            ac=14,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Cleric",
            ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 16, "CHA": 10},
            spells=["Healing Word"],
        )
        cleric.hp = 10

        cleric.cast_spell("Healing Word", target=cleric)

        self.assertGreater(cleric.hp, 10)
        self.assertEqual(cleric.spell_slots_current.get(1), 1)

    def test_fire_bolt_uses_spell_attack_bonus(self):
        dice.roll_die = lambda sides=20: 8
        dice.roll_dice = lambda num, sides: 5
        # Low weapon attack bonus but high INT should still let spell hit AC 13 (8 + 5 = 13)
        wizard = character.Character(
            "Merin",
            hp=14,
            ac=12,
            attack_bonus=1,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            ability_scores={"STR": 8, "DEX": 10, "CON": 10, "INT": 16, "WIS": 10, "CHA": 10},
            spells=["Fire Bolt"],
        )
        target = character.Character("Goblin", hp=20, ac=13, attack_bonus=2, dmg_num=1, dmg_die=6)

        wizard.cast_spell("Fire Bolt", target=target)

        self.assertEqual(target.hp, 15)

    def test_burning_hands_is_marked_aoe(self):
        spell = get_spell_definition("Burning Hands")
        self.assertEqual(spell.get("hit_type"), "aoe")
        self.assertEqual(spell.get("target"), "area")
        self.assertTrue(isinstance(spell.get("aoe"), dict))
        self.assertEqual(spell.get("aoe", {}).get("shape"), "cone")

    def test_thunderwave_is_self_burst_aoe(self):
        spell = get_spell_definition("Thunderwave")
        self.assertEqual(spell.get("hit_type"), "aoe")
        self.assertEqual(spell.get("aoe", {}).get("shape"), "burst_self")

    def test_cast_aoe_spell_hits_multiple_targets_with_one_slot(self):
        dice.roll_dice = lambda num, sides: 6
        caster = character.Character(
            "Merin",
            hp=14,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Burning Hands"],
        )
        t1 = character.Character("Goblin A", hp=12, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)
        t2 = character.Character("Goblin B", hp=12, ac=10, attack_bonus=2, dmg_num=1, dmg_die=6)
        before_slots = caster.spell_slots_current.get(1)

        caster.cast_aoe_spell("Burning Hands", [t1, t2])

        self.assertEqual(caster.spell_slots_current.get(1), before_slots - 1)
        self.assertEqual(t1.hp, 6)
        self.assertEqual(t2.hp, 6)


if __name__ == "__main__":
    unittest.main()
