import unittest

from character import Character


class TestOnHitTriggers(unittest.TestCase):
    def _make_goliath(self, ancestry: str, uses: int = 2) -> Character:
        hero = Character(
            "Hero",
            hp=24,
            ac=14,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=8,
            dmg_bonus=3,
            class_name="Fighter",
            species="Goliath",
            species_traits={"Giant Ancestry": ancestry},
            ability_scores={"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
        )
        hero.giant_ancestry_uses_max = uses
        hero.giant_ancestry_uses_remaining = uses
        return hero

    def _make_target(self) -> Character:
        return Character(
            "Dummy",
            hp=20,
            ac=10,
            attack_bonus=2,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=1,
            class_name="Fighter",
            ability_scores={"STR": 12, "DEX": 12, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
        )

    def test_hill_tumble_is_optional_and_applies_prone_when_used(self):
        hero = self._make_goliath("Hill", uses=2)
        target = self._make_target()

        options = hero.get_on_hit_feature_options(target)
        option_ids = {opt["id"] for opt in options}
        self.assertIn("goliath_hill_tumble", option_ids)
        self.assertEqual(hero.giant_ancestry_uses_remaining, 2)

        result = hero.activate_on_hit_feature("goliath_hill_tumble", target)

        self.assertIn("Hill's Tumble", result)
        self.assertTrue(target.has_status_effect("prone"))
        self.assertEqual(hero.giant_ancestry_uses_remaining, 1)

    def test_no_on_hit_options_when_uses_are_zero(self):
        hero = self._make_goliath("Hill", uses=0)
        target = self._make_target()
        hero.giant_ancestry_uses_remaining = 0

        options = hero.get_on_hit_feature_options(target)

        self.assertEqual(options, [])


if __name__ == "__main__":
    unittest.main()
