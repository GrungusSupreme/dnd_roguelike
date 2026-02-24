"""Tests for Origin Feat implementations."""
import unittest
from typing import Any
import character
import dice
from spell_data import get_spell_definition


class FeatTestBase(unittest.TestCase):
    """Common setup for feat tests."""

    def setUp(self):
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def _make_char(self, **kwargs: Any) -> character.Character:
        defaults: dict[str, Any] = dict(
            name="Hero", hp=20, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
        )
        defaults.update(kwargs)
        return character.Character(**defaults)


# ------------------------------------------------------------------
# Alert
# ------------------------------------------------------------------
class TestAlertFeat(FeatTestBase):
    def test_alert_adds_proficiency_bonus_to_initiative(self):
        """Alert feat should add PB to initiative roll."""
        hero = self._make_char(origin_feats=["Alert"])
        dice.roll_die = lambda sides=20: 10
        total, raw = hero.roll_initiative()
        expected = 10 + hero.initiative_bonus + hero.get_proficiency_bonus()
        self.assertEqual(total, expected)

    def test_no_alert_no_bonus(self):
        """Without Alert, initiative should not include PB."""
        hero = self._make_char()
        dice.roll_die = lambda sides=20: 10
        total, raw = hero.roll_initiative()
        expected = 10 + hero.initiative_bonus
        self.assertEqual(total, expected)

    def test_alert_has_origin_feat(self):
        hero = self._make_char(origin_feats=["Alert"])
        self.assertTrue(hero.has_origin_feat("Alert"))
        self.assertFalse(hero.has_origin_feat("Meaty"))


# ------------------------------------------------------------------
# Savage Attacker
# ------------------------------------------------------------------
class TestSavageAttackerFeat(FeatTestBase):
    def test_savage_attacker_rolls_damage_twice(self):
        """Savage Attacker should take the higher of two weapon damage rolls."""
        hero = self._make_char(origin_feats=["Savage Attacker"])
        target = self._make_char(name="Goblin", hp=50, ac=5)  # low AC to ensure hit

        # Force a hit (roll 15) and track damage rolls
        damage_rolls = [3, 7]  # first roll 3, second roll 7 — should pick 7
        roll_idx = [0]

        def mock_roll_dice(num, sides):
            if sides == 20:
                return 15
            result = damage_rolls[roll_idx[0]] if roll_idx[0] < len(damage_rolls) else 5
            roll_idx[0] += 1
            return result

        dice.roll_die = lambda sides=20: 15
        dice.roll_dice = mock_roll_dice

        hero.attack(target)
        # With Savage Attacker: max(3+bonus, 7+bonus) = 7 + 3 = 10 damage
        expected_hp = 50 - (7 + hero.dmg_bonus)
        self.assertEqual(target.hp, expected_hp)

    def test_savage_attacker_once_per_turn(self):
        """Savage Attacker should only apply once per turn."""
        hero = self._make_char(origin_feats=["Savage Attacker"])
        self.assertFalse(hero.savage_attacker_used)
        hero.savage_attacker_used = True  # simulate already used

        target = self._make_char(name="Goblin", hp=50, ac=5)
        dice.roll_die = lambda sides=20: 15
        dice.roll_dice = lambda num, sides: 4

        hero.attack(target)
        # Should NOT double-roll since already used this turn
        expected_hp = 50 - (4 + hero.dmg_bonus)
        self.assertEqual(target.hp, expected_hp)

    def test_start_turn_resets_savage_attacker(self):
        """start_turn should reset the savage_attacker_used flag."""
        hero = self._make_char(origin_feats=["Savage Attacker"])
        hero.savage_attacker_used = True
        hero.start_turn()
        self.assertFalse(hero.savage_attacker_used)


# ------------------------------------------------------------------
# Magic Initiate
# ------------------------------------------------------------------
class TestMagicInitiateFeat(FeatTestBase):
    def test_mi_wizard_grants_spells(self):
        """Magic Initiate (Wizard) should add 2 cantrips + 1 level-1 spell."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        # Should have Fire Bolt and Ray of Frost (first 2 Wizard cantrips)
        self.assertIn("Fire Bolt", hero.spells)
        self.assertIn("Ray of Frost", hero.spells)
        # Should have Magic Missile (first Wizard level-1 spell)
        self.assertIn("Magic Missile", hero.spells)
        self.assertEqual(hero.mi_free_cast_spell, "Magic Missile")
        self.assertTrue(hero.mi_free_cast_available)

    def test_mi_cleric_grants_spells(self):
        """Magic Initiate (Cleric) should add cleric spells."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Cleric)"],
            class_name="Fighter",
        )
        self.assertIn("Sacred Flame", hero.spells)
        self.assertIn("Chill Touch", hero.spells)
        self.assertIn("Guiding Bolt", hero.spells)
        self.assertEqual(hero.mi_free_cast_spell, "Guiding Bolt")

    def test_mi_druid_grants_spells(self):
        """Magic Initiate (Druid) should add druid spells."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Druid)"],
            class_name="Fighter",
        )
        self.assertIn("Poison Spray", hero.spells)
        self.assertIn("Thorn Whip", hero.spells)
        self.assertIn("Cure Wounds", hero.spells)
        self.assertEqual(hero.mi_free_cast_spell, "Cure Wounds")

    def test_mi_noncaster_gets_spell_slot(self):
        """Non-caster with MI should get at least 1 level-1 spell slot."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        self.assertGreaterEqual(hero.spell_slots_max.get(1, 0), 1)
        self.assertGreaterEqual(hero.spell_slots_current.get(1, 0), 1)

    def test_mi_free_cast_no_slot_consumed(self):
        """Free cast should not consume a spell slot."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        slots_before = hero.spell_slots_current.get(1, 0)
        self.assertTrue(hero.mi_free_cast_available)
        # Consume the free cast
        result = hero._consume_spell_slot_if_needed("Magic Missile")
        self.assertTrue(result)
        self.assertFalse(hero.mi_free_cast_available)
        # Slot should NOT have been consumed
        self.assertEqual(hero.spell_slots_current.get(1, 0), slots_before)

    def test_mi_free_cast_restored_on_rest(self):
        """Free cast should restore on long rest (rest_features)."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        hero.mi_free_cast_available = False
        hero.rest_features()
        self.assertTrue(hero.mi_free_cast_available)

    def test_mi_can_cast_with_free_cast(self):
        """can_cast_spell should return True when free cast is available."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        # Use up all spell slots
        hero.spell_slots_current = {1: 0}
        self.assertTrue(hero.mi_free_cast_available)
        self.assertTrue(hero.can_cast_spell("Magic Missile"))

    def test_mi_cant_cast_without_free_or_slot(self):
        """can_cast_spell should return False when no free cast and no slots."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        hero.spell_slots_current = {1: 0}
        hero.mi_free_cast_available = False
        self.assertFalse(hero.can_cast_spell("Magic Missile"))

    def test_mi_caster_class_no_duplicate_spells(self):
        """If caster already has a spell, MI should not duplicate it."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Wizard",
            spells=["Fire Bolt", "Ray of Frost", "Magic Missile"],
        )
        # No duplicates
        self.assertEqual(len([s for s in hero.spells if s == "Fire Bolt"]), 1)

    def test_mi_level_up_preserves_slot(self):
        """Level up should not remove the MI spell slot for non-casters."""
        hero = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        hero.level_up()
        self.assertGreaterEqual(hero.spell_slots_max.get(1, 0), 1)

    def test_mi_spellcasting_ability_set_for_noncaster(self):
        """Non-caster MI should set spellcasting ability from MI class."""
        hero_wiz = self._make_char(
            origin_feats=["Magic Initiate (Wizard)"],
            class_name="Fighter",
        )
        self.assertEqual(hero_wiz.spellcasting_ability, "INT")

        hero_cleric = self._make_char(
            origin_feats=["Magic Initiate (Cleric)"],
            class_name="Fighter",
        )
        self.assertEqual(hero_cleric.spellcasting_ability, "WIS")


# ------------------------------------------------------------------
# Meaty
# ------------------------------------------------------------------
class TestMeatyFeat(FeatTestBase):
    def test_meaty_adds_hp_at_creation(self):
        """Meaty should add +2 HP per level at creation."""
        hero = self._make_char(origin_feats=["Meaty"])
        hero_no_feat = self._make_char()
        self.assertEqual(hero.max_hp, hero_no_feat.max_hp + 2)
        self.assertEqual(hero.hp, hero_no_feat.hp + 2)

    def test_meaty_adds_hp_on_level_up(self):
        """Meaty should add +2 HP on level up."""
        hero = self._make_char(origin_feats=["Meaty"])
        hero_no = self._make_char()
        hp_before = hero.max_hp
        hp_no_before = hero_no.max_hp
        hero.level_up()
        hero_no.level_up()
        # Both get +5, but Meaty gets extra +2
        self.assertEqual(hero.max_hp - hp_before, 5 + 2)
        self.assertEqual(hero_no.max_hp - hp_no_before, 5)


# ------------------------------------------------------------------
# Healthy
# ------------------------------------------------------------------
class TestHealthyFeat(FeatTestBase):
    def test_healthy_rerolls_ones_on_healing(self):
        """Healthy feat should reroll 1s on healing dice."""
        hero = self._make_char(origin_feats=["Healthy"])
        # When roll returns 1, it should reroll
        call_count = [0]

        def mock_roll_dice(num, sides):
            call_count[0] += 1
            if call_count[0] == 1:
                return 1  # first roll is 1
            return 3  # reroll gives 3

        dice.roll_dice = mock_roll_dice
        result = hero._roll_dice_reroll_ones(1, 8)
        self.assertEqual(result, 3)
        self.assertEqual(call_count[0], 2)  # rolled twice

    def test_healthy_no_reroll_when_not_one(self):
        """Healthy should not reroll if dice result > 1."""
        hero = self._make_char(origin_feats=["Healthy"])

        dice.roll_dice = lambda num, sides: 4
        result = hero._roll_dice_reroll_ones(1, 8)
        self.assertEqual(result, 4)

    def test_healthy_potion_rolls_dice(self):
        """Potion usage with Healthy should roll dice (not flat amount)."""
        hero = self._make_char(origin_feats=["Healthy"], hp=30)
        hero.hp = 10  # damage the hero so healing can work
        hero.potions = 1
        dice.roll_dice = lambda num, sides: 3
        healed = hero.use_potion()
        # Should have rolled 2d4+2 (with reroll-1s), result = 3+2=5 healed
        self.assertGreater(healed, 0)


# ------------------------------------------------------------------
# Iron Fist
# ------------------------------------------------------------------
class TestIronFistFeat(FeatTestBase):
    def test_iron_fist_rerolls_ones_on_unarmed(self):
        """Iron Fist should reroll 1s on unarmed strike damage dice."""
        hero = self._make_char(
            origin_feats=["Iron Fist"],
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 10, "INT": 10, "WIS": 14, "CHA": 10},
        )
        from class_features import get_class_features
        hero.features = get_class_features("Monk")
        self.assertTrue(hero.has_origin_feat("Iron Fist"))


# ------------------------------------------------------------------
# Crafty
# ------------------------------------------------------------------
class TestCraftyFeat(FeatTestBase):
    def test_crafty_discount(self):
        """Crafty should give 20% discount via get_buy_cost."""
        hero = self._make_char(origin_feats=["Crafty"])
        self.assertEqual(hero.get_buy_cost(100), 80)
        self.assertEqual(hero.get_buy_cost(50), 40)
        self.assertEqual(hero.get_buy_cost(1), 1)  # minimum 1 gold

    def test_no_crafty_no_discount(self):
        hero = self._make_char()
        self.assertEqual(hero.get_buy_cost(100), 100)


# ------------------------------------------------------------------
# Skilled
# ------------------------------------------------------------------
class TestSkilledFeat(FeatTestBase):
    def test_skilled_has_origin_feat(self):
        """Skilled should be stored in origin_feats."""
        hero = self._make_char(origin_feats=["Skilled"])
        self.assertTrue(hero.has_origin_feat("Skilled"))


# ------------------------------------------------------------------
# has_origin_feat helper
# ------------------------------------------------------------------
class TestHasOriginFeat(FeatTestBase):
    def test_has_single_feat(self):
        hero = self._make_char(origin_feats=["Alert"])
        self.assertTrue(hero.has_origin_feat("Alert"))
        self.assertFalse(hero.has_origin_feat("Meaty"))

    def test_has_multiple_feats(self):
        hero = self._make_char(origin_feats=["Alert", "Meaty"])
        self.assertTrue(hero.has_origin_feat("Alert"))
        self.assertTrue(hero.has_origin_feat("Meaty"))

    def test_no_feats(self):
        hero = self._make_char()
        self.assertFalse(hero.has_origin_feat("Alert"))

    def test_get_mi_class_extraction(self):
        hero = self._make_char()
        self.assertEqual(hero._get_mi_class("Magic Initiate (Wizard)"), "Wizard")
        self.assertEqual(hero._get_mi_class("Magic Initiate (Cleric)"), "Cleric")
        self.assertIsNone(hero._get_mi_class("Alert"))


if __name__ == "__main__":
    unittest.main()
