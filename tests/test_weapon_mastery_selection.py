import unittest

from character_creation_data import (
    class_has_weapon_mastery,
    class_is_weapon_proficient,
    get_class_weapon_mastery_count,
)
from items import WEAPONS


class TestWeaponMasterySelection(unittest.TestCase):
    def test_level_one_mastery_counts(self):
        self.assertEqual(get_class_weapon_mastery_count("Fighter"), 3)
        self.assertEqual(get_class_weapon_mastery_count("Barbarian"), 2)
        self.assertEqual(get_class_weapon_mastery_count("Rogue"), 2)
        self.assertEqual(get_class_weapon_mastery_count("Wizard"), 0)
        self.assertTrue(class_has_weapon_mastery("Paladin"))
        self.assertFalse(class_has_weapon_mastery("Cleric"))

    def test_rogue_proficiency_filter_for_mastery_choice(self):
        self.assertTrue(class_is_weapon_proficient("Rogue", "Dagger", WEAPONS["Dagger"]))
        self.assertTrue(class_is_weapon_proficient("Rogue", "Rapier", WEAPONS["Rapier"]))
        self.assertFalse(class_is_weapon_proficient("Rogue", "Greataxe", WEAPONS["Greataxe"]))


if __name__ == "__main__":
    unittest.main()
