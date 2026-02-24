import unittest

from character import Character
from items import create_bow, create_greataxe, create_rapier


class TestWeaponModifiers(unittest.TestCase):
    def _make_hero(self) -> Character:
        return Character(
            "Hero",
            hp=20,
            ac=14,
            attack_bonus=0,
            dmg_num=1,
            dmg_die=4,
            dmg_bonus=0,
            class_name="Fighter",
            ability_scores={"STR": 18, "DEX": 12, "CON": 14, "INT": 8, "WIS": 10, "CHA": 10},
        )

    def test_longbow_uses_dex_for_attack_and_damage(self):
        hero = self._make_hero()
        hero.equip_weapon(create_bow())

        self.assertEqual(hero.get_attack_bonus_total(), hero.get_ability_modifier("DEX") + hero.get_proficiency_bonus())
        self.assertEqual(hero.get_damage_bonus(), hero.get_ability_modifier("DEX"))

    def test_greataxe_uses_str_for_attack_and_damage(self):
        hero = self._make_hero()
        hero.equip_weapon(create_greataxe())

        self.assertEqual(hero.get_attack_bonus_total(), hero.get_ability_modifier("STR") + hero.get_proficiency_bonus())
        self.assertEqual(hero.get_damage_bonus(), hero.get_ability_modifier("STR"))

    def test_finesse_weapon_uses_higher_of_str_or_dex(self):
        hero = self._make_hero()
        hero.equip_weapon(create_rapier())

        self.assertEqual(hero.get_attack_bonus_total(), hero.get_ability_modifier("STR") + hero.get_proficiency_bonus())
        self.assertEqual(hero.get_damage_bonus(), hero.get_ability_modifier("STR"))


if __name__ == "__main__":
    unittest.main()
