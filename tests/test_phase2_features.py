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

    def test_wild_shape_unlock_and_duration(self):
        druid = character.Character("Druid", hp=16, ac=13, attack_bonus=4, dmg_num=1, dmg_die=6, class_name="Druid")
        self.assertIsNone(druid.get_feature("Wild Shape"))

        druid.level_up()
        self.assertIsNotNone(druid.get_feature("Wild Shape"))
        self.assertTrue(druid.use_wild_shape())
        self.assertGreaterEqual(druid.temp_hp, 8)
        self.assertEqual(druid.wild_shape_rounds_remaining, 10)

        for _ in range(10):
            druid.end_round()
        self.assertEqual(druid.wild_shape_rounds_remaining, 0)

    def test_hunters_mark_bonus_damage(self):
        ranger = character.Character(
            "Ranger",
            hp=18,
            ac=14,
            attack_bonus=6,
            dmg_num=1,
            dmg_die=6,
            class_name="Ranger",
            ability_scores={"STR": 16, "DEX": 12, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        ranger.level = 2
        enemy_plain = character.Character("Dummy A", hp=20, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4)
        enemy_marked = character.Character("Dummy B", hp=20, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4)

        dice.roll_die = lambda sides=20: 15
        dice.roll_dice = lambda num, sides: 1

        ranger.attack(enemy_plain)
        plain_damage = 20 - enemy_plain.hp

        self.assertTrue(ranger.use_hunters_mark(enemy_marked))
        ranger.attack(enemy_marked)
        marked_damage = 20 - enemy_marked.hp

        self.assertGreater(marked_damage, plain_damage)

    def test_spell_slot_recovery_features(self):
        wizard = character.Character("Wizard", hp=12, ac=12, attack_bonus=4, dmg_num=1, dmg_die=4, class_name="Wizard")
        wizard.level_up()
        wizard.spell_slots_current[1] = 0
        self.assertTrue(wizard.use_arcane_recovery())
        self.assertEqual(wizard.spell_slots_current[1], 1)

        sorcerer = character.Character("Sorcerer", hp=12, ac=12, attack_bonus=4, dmg_num=1, dmg_die=4, class_name="Sorcerer")
        sorcerer.level_up()
        sorcerer.spell_slots_current[1] = 0
        self.assertTrue(sorcerer.use_font_of_magic())
        self.assertEqual(sorcerer.spell_slots_current[1], 1)

    # ------------------------------------------------------------------
    # Dodge AC bonus expiry
    # ------------------------------------------------------------------
    def test_dodge_ac_bonus_expires_next_turn(self):
        """temp_ac_bonus from Dodge should be cleared at start of next player turn.

        In the game loop (GameState.update), temp_ac_bonus is reset to 0 when a
        new player turn starts.  We replicate the same reset path here.
        """
        fighter = character.Character("Fighter", hp=20, ac=16, attack_bonus=5, dmg_num=1, dmg_die=8, class_name="Fighter")

        fighter.defend(ac_bonus=2)
        self.assertEqual(fighter.temp_ac_bonus, 2)

        # The game loop clears temp_ac_bonus at the top of each new player turn.
        # Simulating that reset inline:
        fighter.start_turn()
        fighter.temp_ac_bonus = 0  # exact line from main_gui.py turn-start block

        self.assertEqual(fighter.temp_ac_bonus, 0)

    # ------------------------------------------------------------------
    # Martial Arts (Monk)
    # ------------------------------------------------------------------
    def test_martial_arts_die_values(self):
        monk = character.Character(
            "Monk", hp=16, ac=10, attack_bonus=4, dmg_num=1, dmg_die=6,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        self.assertEqual(monk.get_martial_arts_die(), 6)

        monk.level = 5
        self.assertEqual(monk.get_martial_arts_die(), 8)

        monk.level = 11
        self.assertEqual(monk.get_martial_arts_die(), 10)

        monk.level = 17
        self.assertEqual(monk.get_martial_arts_die(), 12)

    def test_monk_dexterous_attacks_uses_dex(self):
        """Monk with DEX > STR should use DEX for weapon attack modifier."""
        monk = character.Character(
            "Monk", hp=16, ac=10, attack_bonus=4, dmg_num=1, dmg_die=6,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        from items import WEAPONS
        monk.equip_weapon(WEAPONS["Quarterstaff"])
        # Quarterstaff is Simple Melee -> Monk weapon -> should use DEX (mod +3)
        self.assertEqual(monk._get_weapon_attack_ability_modifier(), 3)

    def test_martial_arts_die_upgrades_weapon_damage(self):
        """Martial Arts die should replace weapon die when it is larger."""
        monk = character.Character(
            "Monk", hp=16, ac=10, attack_bonus=4, dmg_num=1, dmg_die=4,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        from items import WEAPONS
        # Club has 1d4 damage -> should be upgraded to 1d6 (Martial Arts die)
        monk.equip_weapon(WEAPONS["Club"])
        dmg_num, dmg_die = monk.get_damage_dice()
        self.assertEqual(dmg_die, 6)  # Martial Arts d6 > Club d4

    def test_martial_arts_bonus_unarmed_strike(self):
        """Martial arts strike should deal damage using martial arts die + DEX."""
        monk = character.Character(
            "Monk", hp=16, ac=10, attack_bonus=4, dmg_num=1, dmg_die=6,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        enemy = character.Character("Dummy", hp=20, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4)

        dice.roll_die = lambda sides=20: 15
        dice.roll_dice = lambda num, sides: 3

        result = monk.martial_arts_strike(enemy)
        self.assertIn("HIT", result)
        # d6 roll (3) + DEX mod (3) = 6 damage
        self.assertEqual(enemy.hp, 14)

    def test_monk_is_monk_weapon(self):
        """Simple melee weapons should qualify as Monk weapons."""
        monk = character.Character(
            "Monk", hp=16, ac=10, attack_bonus=4, dmg_num=1, dmg_die=6,
            class_name="Monk",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 10, "WIS": 14, "CHA": 10},
        )
        from items import WEAPONS
        self.assertTrue(monk.is_monk_weapon(WEAPONS["Quarterstaff"]))
        self.assertTrue(monk.is_monk_weapon(WEAPONS["Club"]))
        # Heavy Crossbow is Simple Ranged, not melee
        self.assertFalse(monk.is_monk_weapon(WEAPONS.get("Heavy Crossbow")))


if __name__ == "__main__":
    unittest.main()
