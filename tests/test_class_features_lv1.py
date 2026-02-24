"""Tests for level-1 class features: Fighting Style, Expertise, Innate Sorcery, Favored Enemy."""

import unittest

import character
import dice
from items import Weapon, Armor


class TestFightingStyleArchery(unittest.TestCase):
    """Archery fighting style: +2 to ranged weapon attack rolls."""

    def test_archery_adds_2_to_ranged_attack(self):
        fighter = character.Character(
            "Archer", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            ability_scores={"STR": 10, "DEX": 16, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            fighting_style="Archery",
        )
        longbow = Weapon(
            name="Longbow", dmg_num=1, dmg_die=8, damage_type="piercing",
            proficiency_type="Martial Ranged", attack_range=15,
            properties=("Two-Handed", "Heavy"), mastery="Slow",
        )
        fighter.equipped_weapon = longbow
        # Expected: DEX(+3) + proficiency(+2) + Archery(+2) = 7
        self.assertEqual(fighter.get_attack_bonus_total(), 7)

    def test_archery_does_not_affect_melee(self):
        fighter = character.Character(
            "Swordfighter", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 10, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            fighting_style="Archery",
        )
        longsword = Weapon(
            name="Longsword", dmg_num=1, dmg_die=8, damage_type="slashing",
            proficiency_type="Martial Melee", attack_range=1,
            properties=("Versatile",), mastery="Sap", versatile_dmg_die=10,
        )
        fighter.equipped_weapon = longsword
        # STR(+3) + proficiency(+2) = 5, no Archery
        self.assertEqual(fighter.get_attack_bonus_total(), 5)


class TestFightingStyleDefense(unittest.TestCase):
    """Defense fighting style: +1 AC while wearing armor."""

    def test_defense_adds_1_ac_with_armor(self):
        fighter = character.Character(
            "Tank", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            fighting_style="Defense",
        )
        chain_mail = Armor(
            name="Chain Mail", ac_base=16, ac_bonus_dex=False,
            proficiency_type="Heavy", weight_lbs=55.0,
        )
        fighter.equipped_armor = chain_mail
        # Chain mail 16 + Defense 1 = 17
        self.assertEqual(fighter.get_ac(), 17)

    def test_defense_does_not_apply_without_armor(self):
        fighter = character.Character(
            "Unarmored", hp=20, ac=10, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            fighting_style="Defense",
        )
        # No armor: 10 + DEX(+2) = 12, no Defense bonus
        self.assertEqual(fighter.get_ac(), 12)


class TestFightingStyleGWF(unittest.TestCase):
    """Great Weapon Fighting: reroll 1s and 2s on damage dice."""

    def setUp(self):
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_dice = self._orig_roll_dice

    def test_gwf_eligible_with_two_handed(self):
        fighter = character.Character(
            "GWF", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=12,
            class_name="Fighter",
            fighting_style="Great Weapon Fighting",
        )
        greataxe = Weapon(
            name="Greataxe", dmg_num=1, dmg_die=12, damage_type="slashing",
            proficiency_type="Martial Melee", attack_range=1,
            properties=("Two-Handed", "Heavy"), mastery="Cleave",
        )
        fighter.equipped_weapon = greataxe
        self.assertTrue(fighter._is_gwf_eligible())

    def test_gwf_eligible_with_versatile_no_offhand(self):
        fighter = character.Character(
            "GWF", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            fighting_style="Great Weapon Fighting",
        )
        longsword = Weapon(
            name="Longsword", dmg_num=1, dmg_die=8, damage_type="slashing",
            proficiency_type="Martial Melee", attack_range=1,
            properties=("Versatile",), mastery="Sap", versatile_dmg_die=10,
        )
        fighter.equipped_weapon = longsword
        fighter.equipped_offhand = None
        self.assertTrue(fighter._is_gwf_eligible())

    def test_gwf_not_eligible_versatile_with_shield(self):
        fighter = character.Character(
            "GWF", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
            fighting_style="Great Weapon Fighting",
        )
        longsword = Weapon(
            name="Longsword", dmg_num=1, dmg_die=8, damage_type="slashing",
            proficiency_type="Martial Melee", attack_range=1,
            properties=("Versatile",), mastery="Sap", versatile_dmg_die=10,
        )
        fighter.equipped_weapon = longsword
        fighter.equipped_offhand = Armor(name="Shield", ac_base=2)  # Shield
        self.assertFalse(fighter._is_gwf_eligible())

    def test_gwf_roll_dice_rerolls_low(self):
        fighter = character.Character(
            "GWF", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=12,
            class_name="Fighter",
            fighting_style="Great Weapon Fighting",
        )
        # Mock dice: always returns 1 (which should become 3 via GWF)
        dice.roll_dice = lambda num, die: 1
        result = fighter._roll_gwf_dice(2, 12)
        # Each die rolls 1, treated as 3 -> total 6
        self.assertEqual(result, 6)

    def test_gwf_roll_dice_keeps_high(self):
        fighter = character.Character(
            "GWF", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=12,
            class_name="Fighter",
            fighting_style="Great Weapon Fighting",
        )
        # Mock dice: returns 5 (kept as-is)
        dice.roll_dice = lambda num, die: 5
        result = fighter._roll_gwf_dice(2, 12)
        self.assertEqual(result, 10)


class TestExpertise(unittest.TestCase):
    """Expertise doubles proficiency bonus on chosen skills."""

    def test_expertise_doubles_proficiency(self):
        rogue = character.Character(
            "Sneaky", hp=16, ac=14, attack_bonus=5, dmg_num=1, dmg_die=6,
            class_name="Rogue",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
            skill_proficiencies=["Stealth", "Perception"],
            expertise_skills=["Stealth"],
        )
        # Stealth: DEX(+3) + proficiency(+2) * 2 = +7
        self.assertEqual(rogue.get_skill_bonus("Stealth"), 7)

    def test_proficiency_without_expertise(self):
        rogue = character.Character(
            "Sneaky", hp=16, ac=14, attack_bonus=5, dmg_num=1, dmg_die=6,
            class_name="Rogue",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
            skill_proficiencies=["Stealth", "Perception"],
            expertise_skills=["Stealth"],
        )
        # Perception: WIS(+0) + proficiency(+2) = +2 (no expertise)
        self.assertEqual(rogue.get_skill_bonus("Perception"), 2)

    def test_no_proficiency_gets_ability_mod_only(self):
        rogue = character.Character(
            "Sneaky", hp=16, ac=14, attack_bonus=5, dmg_num=1, dmg_die=6,
            class_name="Rogue",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
            skill_proficiencies=["Stealth"],
            expertise_skills=["Stealth"],
        )
        # Athletics: STR(+0), not proficient
        self.assertEqual(rogue.get_skill_bonus("Athletics"), 0)


class TestInnateSorcery(unittest.TestCase):
    """Innate Sorcery: bonus action activation, +1 spell DC, advantage on spell attacks."""

    def test_activate_innate_sorcery(self):
        sorc = character.Character(
            "Sorc", hp=14, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Sorcerer",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 10, "WIS": 10, "CHA": 16},
        )
        self.assertFalse(sorc.innate_sorcery_active)
        result = sorc.activate_innate_sorcery()
        self.assertTrue(result)
        self.assertTrue(sorc.innate_sorcery_active)
        self.assertEqual(sorc.innate_sorcery_rounds_remaining, 10)

    def test_cannot_activate_twice(self):
        sorc = character.Character(
            "Sorc", hp=14, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Sorcerer",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 10, "WIS": 10, "CHA": 16},
        )
        sorc.activate_innate_sorcery()
        result = sorc.activate_innate_sorcery()
        self.assertFalse(result)  # Already active

    def test_innate_sorcery_boosts_spell_dc(self):
        sorc = character.Character(
            "Sorc", hp=14, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Sorcerer",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 10, "WIS": 10, "CHA": 16},
        )
        base_dc = sorc.get_spell_save_dc()  # 8 + 2 + 3 = 13
        self.assertEqual(base_dc, 13)
        sorc.activate_innate_sorcery()
        boosted_dc = sorc.get_spell_save_dc()
        self.assertEqual(boosted_dc, 14)  # +1

    def test_innate_sorcery_dc_only_for_sorcerer(self):
        wizard = character.Character(
            "Wiz", hp=12, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Wizard",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 16, "WIS": 10, "CHA": 10},
        )
        base_dc = wizard.get_spell_save_dc()  # 8 + 2 + 3 = 13
        wizard.innate_sorcery_active = True  # Force it on
        self.assertEqual(wizard.get_spell_save_dc(), base_dc)  # No bonus

    def test_innate_sorcery_ticks_down_each_round(self):
        sorc = character.Character(
            "Sorc", hp=14, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Sorcerer",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 10, "WIS": 10, "CHA": 16},
        )
        sorc.activate_innate_sorcery()
        self.assertEqual(sorc.innate_sorcery_rounds_remaining, 10)
        sorc.end_round()
        self.assertEqual(sorc.innate_sorcery_rounds_remaining, 9)
        # Tick down to 0
        for _ in range(9):
            sorc.end_round()
        self.assertFalse(sorc.innate_sorcery_active)
        self.assertEqual(sorc.innate_sorcery_rounds_remaining, 0)

    def test_innate_sorcery_resets_on_rest(self):
        sorc = character.Character(
            "Sorc", hp=14, ac=10, attack_bonus=3, dmg_num=1, dmg_die=6,
            class_name="Sorcerer",
            ability_scores={"STR": 8, "DEX": 14, "CON": 12, "INT": 10, "WIS": 10, "CHA": 16},
        )
        sorc.activate_innate_sorcery()
        self.assertTrue(sorc.innate_sorcery_active)
        sorc.rest_features()
        self.assertFalse(sorc.innate_sorcery_active)
        self.assertEqual(sorc.innate_sorcery_rounds_remaining, 0)


class TestFavoredEnemy(unittest.TestCase):
    """Favored Enemy: Hunter's Mark for Rangers at level 1 with 2 free casts/LR."""

    def test_ranger_gets_free_casts(self):
        ranger = character.Character(
            "Ranger", hp=18, ac=14, attack_bonus=4, dmg_num=1, dmg_die=8,
            class_name="Ranger",
            ability_scores={"STR": 14, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        self.assertEqual(ranger.favored_enemy_free_casts, 2)
        self.assertEqual(ranger.favored_enemy_free_casts_max, 2)

    def test_non_ranger_has_no_free_casts(self):
        fighter = character.Character(
            "Fighter", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8,
            class_name="Fighter",
        )
        self.assertEqual(fighter.favored_enemy_free_casts, 0)

    def test_hunters_mark_uses_free_casts_first(self):
        ranger = character.Character(
            "Ranger", hp=18, ac=14, attack_bonus=4, dmg_num=1, dmg_die=8,
            class_name="Ranger",
            ability_scores={"STR": 14, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        target = character.Character("Goblin", hp=7, ac=13, attack_bonus=2, dmg_num=1, dmg_die=6)

        # First use: free cast
        result = ranger.use_hunters_mark(target)
        self.assertTrue(result)
        self.assertEqual(ranger.favored_enemy_free_casts, 1)

        # Second use: free cast
        target2 = character.Character("Orc", hp=15, ac=13, attack_bonus=3, dmg_num=1, dmg_die=8)
        result = ranger.use_hunters_mark(target2)
        self.assertTrue(result)
        self.assertEqual(ranger.favored_enemy_free_casts, 0)

    def test_free_casts_reset_on_rest(self):
        ranger = character.Character(
            "Ranger", hp=18, ac=14, attack_bonus=4, dmg_num=1, dmg_die=8,
            class_name="Ranger",
            ability_scores={"STR": 14, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        target = character.Character("Goblin", hp=7, ac=13, attack_bonus=2, dmg_num=1, dmg_die=6)
        ranger.use_hunters_mark(target)
        ranger.use_hunters_mark(target)
        self.assertEqual(ranger.favored_enemy_free_casts, 0)
        ranger.rest_features()
        self.assertEqual(ranger.favored_enemy_free_casts, 2)


class TestBarbarianRage(unittest.TestCase):
    """Rage maintenance per SRD 5.2.1: must attack, force save, or use bonus action to extend."""

    def _make_barbarian(self):
        return character.Character(
            "Grognak", hp=20, ac=14, attack_bonus=5, dmg_num=1, dmg_die=12,
            class_name="Barbarian",
            ability_scores={"STR": 16, "DEX": 14, "CON": 16, "INT": 8, "WIS": 10, "CHA": 8},
        )

    def setUp(self):
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_rage_activates_via_start_combat(self):
        barb = self._make_barbarian()
        msgs = barb.start_combat(auto_features=True)
        self.assertTrue(barb.raging)
        self.assertEqual(barb.rage_rounds_remaining, 10)
        self.assertTrue(barb.rage_extended_this_turn)
        self.assertTrue(any("Rage" in m for m in msgs))

    def test_rage_ends_if_not_maintained(self):
        """If barbarian does nothing on a turn, rage ends at end of round."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        # Simulate turn 2: start turn resets extended flag
        barb.start_turn()
        self.assertFalse(barb.rage_extended_this_turn)
        # End round without attacking or extending
        msgs = barb.end_round()
        self.assertFalse(barb.raging)
        self.assertTrue(any("not maintained" in m for m in msgs))

    def test_rage_persists_when_attacking(self):
        """Attacking an enemy extends rage automatically."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        enemy = character.Character("Goblin", hp=10, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4)
        # Turn 2
        barb.start_turn()
        dice.roll_die = lambda *a, **k: 15  # ensure hit
        dice.roll_dice = lambda *a, **k: 5
        barb.attack(enemy)
        self.assertTrue(barb.rage_extended_this_turn)
        msgs = barb.end_round()
        self.assertTrue(barb.raging)
        self.assertFalse(any("not maintained" in m for m in msgs))

    def test_rage_persists_when_extended_by_bonus_action(self):
        """Using bonus action to extend rage keeps it going."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        # Turn 2: no attack, but extend via bonus action
        barb.start_turn()
        self.assertFalse(barb.rage_extended_this_turn)
        result = barb.extend_rage()
        self.assertTrue(result)
        self.assertTrue(barb.rage_extended_this_turn)
        msgs = barb.end_round()
        self.assertTrue(barb.raging)

    def test_extend_rage_fails_when_not_raging(self):
        barb = self._make_barbarian()
        self.assertFalse(barb.extend_rage())

    def test_rage_ends_at_max_duration(self):
        """Rage ends after 10 rounds even if maintained every turn."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        for _ in range(10):
            barb.start_turn()
            barb.rage_extended_this_turn = True
            barb.end_round()
        self.assertFalse(barb.raging)

    def test_rage_grants_resistance(self):
        """Raging halves physical damage."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        taken, resisted = barb.take_damage(10, damage_type="slashing")
        self.assertTrue(resisted)
        self.assertEqual(taken, 5)

    def test_rage_bonus_damage(self):
        """Raging adds +2 to Strength-based melee damage."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        enemy = character.Character("Dummy", hp=100, ac=5, attack_bonus=0, dmg_num=1, dmg_die=4)
        dice.roll_die = lambda *a, **k: 20  # guarantee crit
        dice.roll_dice = lambda *a, **k: 6
        result = barb.attack(enemy)
        self.assertIn("Rage +2", result)

    def test_activate_rage_uses_feature_charge(self):
        barb = self._make_barbarian()
        rage_feature = barb.get_feature("Rage")
        self.assertIsNotNone(rage_feature)
        initial_uses = rage_feature.uses_remaining
        barb.activate_rage()
        self.assertEqual(rage_feature.uses_remaining, initial_uses - 1)
        self.assertTrue(barb.raging)

    def test_cannot_activate_rage_while_already_raging(self):
        barb = self._make_barbarian()
        barb.activate_rage()
        self.assertFalse(barb.activate_rage())

    def test_rage_attack_miss_still_extends(self):
        """Even a miss counts as 'making an attack roll' for rage maintenance."""
        barb = self._make_barbarian()
        barb.start_combat(auto_features=True)
        enemy = character.Character("Dragon", hp=100, ac=30, attack_bonus=0, dmg_num=1, dmg_die=4)
        barb.start_turn()
        dice.roll_die = lambda *a, **k: 2  # very likely miss
        dice.roll_dice = lambda *a, **k: 1
        barb.attack(enemy)
        self.assertTrue(barb.rage_extended_this_turn)
        msgs = barb.end_round()
        self.assertTrue(barb.raging)


if __name__ == "__main__":
    unittest.main()
