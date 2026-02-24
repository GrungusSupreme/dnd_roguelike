import unittest
from unittest.mock import patch

from character import Character
from items import ARMOR, WEAPONS


class TestEquipmentTables(unittest.TestCase):
    def test_weapons_table_contains_full_srd_set(self):
        required = {
            "Club", "Dagger", "Greatclub", "Handaxe", "Javelin", "Light Hammer", "Mace", "Quarterstaff", "Sickle", "Spear",
            "Dart", "Light Crossbow", "Shortbow", "Sling",
            "Battleaxe", "Flail", "Glaive", "Greataxe", "Greatsword", "Halberd", "Lance", "Longsword", "Maul", "Morningstar", "Pike", "Rapier", "Scimitar", "Shortsword", "Trident", "Warhammer", "War Pick", "Whip",
            "Blowgun", "Hand Crossbow", "Heavy Crossbow", "Longbow", "Musket", "Pistol",
        }
        self.assertTrue(required.issubset(set(WEAPONS.keys())))

    def test_armor_table_contains_full_srd_set(self):
        required = {
            "Padded Armor", "Leather Armor", "Studded Leather Armor",
            "Hide Armor", "Chain Shirt", "Scale Mail", "Breastplate", "Half Plate Armor",
            "Ring Mail", "Chain Mail", "Splint Armor", "Plate Armor",
        }
        self.assertTrue(required.issubset(set(ARMOR.keys())))

    def _make_character(
        self,
        name: str,
        str_score: int = 16,
        dex_score: int = 12,
        class_name: str = "Fighter",
        weapon_masteries=None,
    ) -> Character:
        return Character(
            name,
            hp=20,
            ac=12,
            attack_bonus=2,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=0,
            class_name=class_name,
            ability_scores={"STR": str_score, "DEX": dex_score, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            weapon_masteries=weapon_masteries or [],
        )

    def test_graze_mastery_applies_on_miss(self):
        attacker = self._make_character("Hero", str_score=16, weapon_masteries=["Glaive"])
        target = self._make_character("Target")
        target.ac = 99
        attacker.equip_weapon(WEAPONS["Glaive"])

        with patch.object(Character, "roll_d20", return_value=2):
            attacker.attack(target)

        self.assertEqual(target.hp, target.max_hp - 3)

    def test_sap_and_slow_masteries_apply_statuses(self):
        attacker = self._make_character("Hero", weapon_masteries=["Mace", "Club"])
        target = self._make_character("Target")

        attacker.equip_weapon(WEAPONS["Mace"])
        with patch.object(Character, "roll_d20", return_value=20):
            attacker.attack(target)
        self.assertTrue(target.has_status_effect("sapped"))

        attacker.equip_weapon(WEAPONS["Club"])
        with patch.object(Character, "roll_d20", return_value=20):
            attacker.attack(target)
        self.assertTrue(target.has_status_effect("slowed"))

    def test_heavy_weapon_can_force_disadvantage(self):
        attacker = self._make_character("Hero", str_score=10, dex_score=10)
        target = self._make_character("Target")
        target.ac = 14
        attacker.equip_weapon(WEAPONS["Greataxe"])

        with patch.object(Character, "roll_d20", side_effect=[18, 2]):
            result = attacker.attack(target)

        self.assertIn("-> MISS", result)

    def test_mastery_not_applied_when_not_chosen(self):
        attacker = self._make_character("Hero", class_name="Fighter", weapon_masteries=[])
        target = self._make_character("Target")
        attacker.equip_weapon(WEAPONS["Mace"])

        with patch.object(Character, "roll_d20", return_value=20):
            attacker.attack(target)

        self.assertFalse(target.has_status_effect("sapped"))


if __name__ == "__main__":
    unittest.main()
