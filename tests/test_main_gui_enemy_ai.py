import unittest

from character import Character
from main_gui import GameState


class TestMainGuiEnemyAI(unittest.TestCase):
    def _make_character(self, name: str, hp: int = 20, attack_range: int = 1) -> Character:
        return Character(
            name,
            hp=hp,
            ac=10,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            dmg_bonus=2,
            class_name="Fighter",
            attack_range=attack_range,
        )

    def test_enemies_move_by_speed_tiles(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin")
        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (30, 30)
        state.enemy_positions = {enemy: (10, 10)}
        state.rocks = set()

        start = state.enemy_positions[enemy]
        start_dist = max(abs(start[0] - 30), abs(start[1] - 30))
        state.move_enemies()
        end = state.enemy_positions[enemy]
        end_dist = max(abs(end[0] - 30), abs(end[1] - 30))

        self.assertEqual(start_dist - end_dist, 6)

    def test_enemy_pursues_player_not_keep_gate(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin")
        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (0, 0)
        state.enemy_positions = {enemy: (32, 0)}
        state.rocks = set()

        state.move_enemies()
        ex, ey = state.enemy_positions[enemy]

        self.assertLess(ex, 32)
        self.assertEqual(ey, 0)

    def test_hidden_player_uses_last_known_position(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin")
        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (40, 40)
        state.hidden = True
        state.last_known_player_pos = (5, 5)
        state.enemy_positions = {enemy: (20, 20)}
        state.rocks = set()

        start_dist = max(abs(20 - 5), abs(20 - 5))
        state.move_enemies()
        ex, ey = state.enemy_positions[enemy]
        end_dist = max(abs(ex - 5), abs(ey - 5))

        self.assertLess(end_dist, start_dist)

    def test_hide_success_when_stealth_beats_passive_perception(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin")
        enemy.passive_perception = 10

        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (24, 20)}
        state.rocks = set()
        state.trees = set()
        player.roll_d20 = lambda: 15

        success, _ = state.attempt_hide()

        self.assertTrue(success)
        self.assertTrue(state.hidden)
        self.assertIsNotNone(state.hidden_stealth_total)

    def test_hide_fails_when_enemy_can_see_and_passive_is_higher(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin")
        enemy.passive_perception = 15

        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (24, 20)}
        state.rocks = set()
        state.trees = set()
        player.roll_d20 = lambda: 5

        success, _ = state.attempt_hide()

        self.assertFalse(success)
        self.assertFalse(state.hidden)
        self.assertIsNone(state.hidden_stealth_total)

    def test_hidden_player_not_revealed_when_obscured_by_tree(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin", attack_range=1)
        enemy.passive_perception = 18
        enemy.attack = lambda target, log_fn=None, target_distance=None: "-> MISS"

        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (24, 20)}
        state.rocks = set()
        state.trees = {(22, 20)}
        state.hidden = True
        state.hidden_stealth_total = 8

        state.resolve_combat()

        self.assertTrue(state.hidden)

    def test_hidden_player_revealed_when_enemy_has_clear_sight(self):
        player = self._make_character("Hero")
        enemy = self._make_character("Goblin", attack_range=1)
        enemy.passive_perception = 14
        enemy.attack = lambda target, log_fn=None, target_distance=None: "-> MISS"

        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (24, 20)}
        state.rocks = set()
        state.trees = set()
        state.hidden = True
        state.hidden_stealth_total = 12

        state.resolve_combat()

        self.assertFalse(state.hidden)
        self.assertIsNone(state.hidden_stealth_total)

    def test_targeted_spell_reveals_hidden_player(self):
        player = Character(
            "Mage",
            hp=18,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Fire Bolt"],
        )
        enemy = self._make_character("Goblin")
        enemy.ac = 8

        state = GameState(player)
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (22, 20)}
        state.rocks = set()
        state.trees = set()
        state.hidden = True
        state.hidden_stealth_total = 18
        player.roll_d20 = lambda: 20

        acted = state.cast_spell_at("Fire Bolt", (22, 20))

        self.assertTrue(acted)
        self.assertFalse(state.hidden)
        self.assertIsNone(state.hidden_stealth_total)

    def test_aoe_spell_reveals_hidden_player(self):
        player = Character(
            "Mage",
            hp=18,
            ac=12,
            attack_bonus=4,
            dmg_num=1,
            dmg_die=6,
            class_name="Wizard",
            spells=["Thunderwave"],
        )

        state = GameState(player)
        state.enemies = []
        state.player_pos = (20, 20)
        state.enemy_positions = {}
        state.rocks = set()
        state.trees = set()
        state.hidden = True
        state.hidden_stealth_total = 18

        acted = state.cast_aoe_spell_at("Thunderwave", (20, 20))

        self.assertTrue(acted)
        self.assertFalse(state.hidden)
        self.assertIsNone(state.hidden_stealth_total)


if __name__ == "__main__":
    unittest.main()
