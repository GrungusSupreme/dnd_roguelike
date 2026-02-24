import unittest
from unittest.mock import patch

from character import Character
from main_gui import GameState


class TestMainGuiRewards(unittest.TestCase):
    def _make_character(self, name: str, hp: int, bounty: int = 0) -> Character:
        return Character(
            name,
            hp=hp,
            ac=10,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 12, "CON": 14, "INT": 10, "WIS": 10, "CHA": 10},
            bounty=bounty,
        )

    def test_defeat_rewards_accumulate_gold_and_xp(self):
        player = self._make_character("Hero", hp=20)
        state = GameState(player)
        enemy = self._make_character("Goblin", hp=1, bounty=4)

        with patch("main_gui.random.randint", return_value=99):
            gold_gain, xp_gain, item_drop = state._apply_enemy_defeat_rewards(enemy)

        self.assertEqual(gold_gain, 4)
        self.assertEqual(xp_gain, 40)
        self.assertIsNone(item_drop)
        self.assertEqual(state.wave_gold_gained, 4)
        self.assertEqual(state.wave_xp_gained, 40)
        self.assertEqual(player.gold, 4)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.xp, 40)
        self.assertEqual(state.banked_xp_total, 0)
        self.assertIn("Gold gained: 4", state.wave_loot_lines())
        self.assertIn("XP gained: 40", state.wave_loot_lines())
        self.assertFalse(any("Level-1 focus:" in line for line in state.wave_loot_lines()))

    def test_defeat_rewards_can_drop_potion(self):
        player = self._make_character("Hero", hp=20)
        state = GameState(player)
        enemy = self._make_character("Goblin", hp=1, bounty=3)

        with patch("main_gui.random.randint", return_value=1):
            _, _, item_drop = state._apply_enemy_defeat_rewards(enemy)

        self.assertIsNotNone(item_drop)
        self.assertGreaterEqual(player.potions, 1)
        loot_lines = state.wave_loot_lines()
        self.assertTrue(any(line.startswith("Item: ") for line in loot_lines))

    def test_can_enable_level_one_focus_and_bank_xp(self):
        player = self._make_character("Hero", hp=20)
        state = GameState(player, level_one_focus=True)
        enemy = self._make_character("Goblin", hp=1, bounty=4)

        with patch("main_gui.random.randint", return_value=99):
            gold_gain, xp_gain, _ = state._apply_enemy_defeat_rewards(enemy)

        self.assertEqual(gold_gain, 4)
        self.assertEqual(xp_gain, 40)
        self.assertEqual(player.xp, 0)
        self.assertEqual(state.banked_xp_total, 40)

    def test_reward_level_up_creates_pending_event_with_new_features(self):
        player = self._make_character("Hero", hp=20)
        state = GameState(player)
        enemy = self._make_character("Champion", hp=1, bounty=10)

        with patch("main_gui.random.randint", return_value=99):
            _, xp_gain, _ = state._apply_enemy_defeat_rewards(enemy)

        self.assertEqual(xp_gain, 100)
        self.assertEqual(player.level, 2)
        self.assertEqual(len(state.pending_level_up_events), 1)
        event = state.pending_level_up_events[0]
        self.assertEqual(event.get("from_level"), 1)
        self.assertEqual(event.get("to_level"), 2)
        features = event.get("features", [])
        assert isinstance(features, list)
        self.assertIn("Action Surge", features)

    def test_cunning_action_available_for_level_two_rogue(self):
        rogue = Character(
            "Rogue",
            hp=18,
            ac=14,
            attack_bonus=5,
            dmg_num=1,
            dmg_die=6,
            class_name="Rogue",
            ability_scores={"STR": 10, "DEX": 16, "CON": 12, "INT": 12, "WIS": 12, "CHA": 10},
        )
        rogue.level = 2
        state = GameState(rogue)

        state.spend_action()
        self.assertTrue(state.can_use_cunning_action())
        spend_type = state.spend_action_or_cunning_bonus()
        self.assertEqual(spend_type, "bonus")
        self.assertTrue(state.spent_bonus_action)


if __name__ == "__main__":
    unittest.main()
