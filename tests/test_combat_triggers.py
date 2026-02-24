"""Tests for the mid-combat trigger confirmation system.

Covers:
- Trigger queue mechanics (queue, resolve, modal generation)
- Attack of Opportunity detection during enemy movement
- Weapon mastery trigger queueing (Push / Cleave / Nick)
- On-hit species feature triggers (Goliath ancestry)
- Reaction economy (one per round, resets on turn start)
"""

import unittest
from unittest.mock import patch

from character import Character
from main_gui import GameState
from items import Weapon, WEAPONS


class TestTriggerQueue(unittest.TestCase):
    """Basic trigger queue mechanics."""

    def _make_state(self) -> GameState:
        player = Character(
            "Hero", hp=30, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
        )
        return GameState(player)

    def test_queue_and_get_modal(self):
        state = self._make_state()
        state.queue_trigger({
            "title": "Test Trigger",
            "description": ["Line 1", "Line 2"],
            "accept_label": "Yes",
            "decline_label": "No",
            "on_accept": lambda: None,
        })
        self.assertEqual(len(state.pending_triggers), 1)
        modal = state.get_current_trigger_modal()
        self.assertIsNotNone(modal)
        assert modal is not None
        self.assertEqual(modal["title"], "Test Trigger")
        self.assertEqual(len(modal["buttons"]), 2)
        self.assertEqual(modal["buttons"][0], ("trigger_accept", "Yes"))
        self.assertEqual(modal["buttons"][1], ("trigger_decline", "No"))

    def test_resolve_accept_calls_callback(self):
        state = self._make_state()
        called = {"accept": False}
        state.queue_trigger({
            "title": "T",
            "description": [],
            "accept_label": "Y",
            "decline_label": "N",
            "on_accept": lambda: called.__setitem__("accept", True),
        })
        state.resolve_current_trigger(accepted=True)
        self.assertTrue(called["accept"])
        self.assertEqual(len(state.pending_triggers), 0)

    def test_resolve_decline_calls_callback(self):
        state = self._make_state()
        called = {"decline": False}
        state.queue_trigger({
            "title": "T",
            "description": [],
            "accept_label": "Y",
            "decline_label": "N",
            "on_decline": lambda: called.__setitem__("decline", True),
        })
        state.resolve_current_trigger(accepted=False)
        self.assertTrue(called["decline"])

    def test_no_modal_when_empty(self):
        state = self._make_state()
        self.assertIsNone(state.get_current_trigger_modal())

    def test_multiple_triggers_resolved_in_order(self):
        state = self._make_state()
        order = []
        state.queue_trigger({
            "title": "First",
            "description": [],
            "accept_label": "Y",
            "decline_label": "N",
            "on_accept": lambda: order.append("first"),
        })
        state.queue_trigger({
            "title": "Second",
            "description": [],
            "accept_label": "Y",
            "decline_label": "N",
            "on_accept": lambda: order.append("second"),
        })
        state.resolve_current_trigger(accepted=True)
        state.resolve_current_trigger(accepted=True)
        self.assertEqual(order, ["first", "second"])


class TestAttackOfOpportunity(unittest.TestCase):
    """AoO trigger detection when enemies leave player melee reach."""

    def _make_melee_fighter(self) -> Character:
        player = Character(
            "Hero", hp=30, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
        )
        # Equip a melee weapon
        weapon = WEAPONS.get("Longsword")
        if weapon:
            player.equipped_weapon = weapon
        return player

    def _make_enemy(self, name="Goblin", hp=10) -> Character:
        return Character(
            name, hp=hp, ac=12, attack_bonus=3,
            dmg_num=1, dmg_die=6, dmg_bonus=1,
            class_name="Fighter",
        )

    def test_aoo_queued_when_enemy_leaves_reach(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.player_pos = (20, 20)
        enemy = self._make_enemy()
        state.enemies = [enemy]

        # Enemy was adjacent (in reach), now moved away
        pre_move = {enemy: (20, 21)}  # 1 tile away = in reach
        state.enemy_positions = {enemy: (20, 23)}  # 3 tiles away = out of reach

        state._check_aoo_triggers(pre_move)
        self.assertEqual(len(state.pending_triggers), 1)
        self.assertIn("Attack of Opportunity", state.pending_triggers[0]["title"])

    def test_no_aoo_when_enemy_stays_in_reach(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.player_pos = (20, 20)
        enemy = self._make_enemy()
        state.enemies = [enemy]

        # Enemy stays adjacent
        pre_move = {enemy: (20, 21)}
        state.enemy_positions = {enemy: (21, 20)}

        state._check_aoo_triggers(pre_move)
        self.assertEqual(len(state.pending_triggers), 0)

    def test_no_aoo_when_reaction_used(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.player_pos = (20, 20)
        state.reaction_used = True
        enemy = self._make_enemy()
        state.enemies = [enemy]

        pre_move = {enemy: (20, 21)}
        state.enemy_positions = {enemy: (20, 23)}

        state._check_aoo_triggers(pre_move)
        self.assertEqual(len(state.pending_triggers), 0)

    def test_aoo_accept_uses_reaction(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.player_pos = (20, 20)
        enemy = self._make_enemy(hp=100)
        state.enemies = [enemy]

        pre_move = {enemy: (20, 21)}
        state.enemy_positions = {enemy: (20, 23)}

        state._check_aoo_triggers(pre_move)
        self.assertFalse(state.reaction_used)

        # Accept the AoO
        state.resolve_current_trigger(accepted=True)
        self.assertTrue(state.reaction_used)

    def test_reaction_resets_on_turn_start(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.reaction_used = True
        state.player_turn_started = False
        state.turn_phase = "player_input"

        # Simulate update which starts the turn
        class FakeWindow:
            running = True
        state.update(FakeWindow())  # type: ignore[arg-type]

        self.assertFalse(state.reaction_used)

    def test_no_aoo_when_enemy_was_not_in_reach(self):
        player = self._make_melee_fighter()
        state = GameState(player)
        state.player_pos = (20, 20)
        enemy = self._make_enemy()
        state.enemies = [enemy]

        # Enemy was already out of reach
        pre_move = {enemy: (20, 25)}
        state.enemy_positions = {enemy: (20, 28)}

        state._check_aoo_triggers(pre_move)
        self.assertEqual(len(state.pending_triggers), 0)


class TestWeaponMasteryTriggers(unittest.TestCase):
    """Weapon mastery confirmations (Push / Cleave / Nick)."""

    def _make_state_with_weapon(self, weapon_name: str) -> tuple[GameState, Character]:
        player = Character(
            "Hero", hp=30, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
        )
        weapon = WEAPONS.get(weapon_name)
        if weapon:
            player.equipped_weapon = weapon
        return GameState(player), player

    def _make_enemy(self, name="Goblin", hp=20) -> Character:
        return Character(
            name, hp=hp, ac=8, attack_bonus=3,
            dmg_num=1, dmg_die=6, dmg_bonus=1,
            class_name="Fighter",
        )

    def test_push_mastery_queues_trigger(self):
        state, player = self._make_state_with_weapon("Greatclub")
        enemy = self._make_enemy()
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (20, 21)}

        state._queue_weapon_mastery_trigger(enemy, "push")
        self.assertEqual(len(state.pending_triggers), 1)
        self.assertIn("Push", state.pending_triggers[0]["title"])

    def test_cleave_mastery_queues_trigger_with_adjacent_target(self):
        state, player = self._make_state_with_weapon("Greataxe")
        enemy1 = self._make_enemy("Goblin1")
        enemy2 = self._make_enemy("Goblin2")
        state.enemies = [enemy1, enemy2]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy1: (20, 21), enemy2: (21, 21)}

        state._queue_weapon_mastery_trigger(enemy1, "cleave")
        self.assertEqual(len(state.pending_triggers), 1)
        self.assertIn("Cleave", state.pending_triggers[0]["title"])

    def test_cleave_mastery_no_trigger_without_adjacent_target(self):
        state, player = self._make_state_with_weapon("Greataxe")
        enemy1 = self._make_enemy("Goblin1")
        state.enemies = [enemy1]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy1: (20, 21)}

        state._queue_weapon_mastery_trigger(enemy1, "cleave")
        self.assertEqual(len(state.pending_triggers), 0)

    def test_nick_mastery_queues_trigger_with_offhand(self):
        state, player = self._make_state_with_weapon("Scimitar")
        offhand = WEAPONS.get("Dagger")
        assert offhand is not None
        player.equipped_offhand = offhand  # type: ignore[assignment]
        enemy = self._make_enemy()
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (20, 21)}

        state._queue_weapon_mastery_trigger(enemy, "nick")
        self.assertEqual(len(state.pending_triggers), 1)
        self.assertIn("Nick", state.pending_triggers[0]["title"])


class TestOnHitSpeciesTriggers(unittest.TestCase):
    """On-hit species feature triggers (Goliath ancestry)."""

    def _make_goliath_player(self, ancestry="fire") -> Character:
        player = Character(
            "Hero", hp=30, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
            species="Goliath",
            species_traits={"Giant Ancestry": ancestry},
        )
        player.giant_ancestry = ancestry
        player.giant_ancestry_uses_remaining = 2
        player.giant_ancestry_uses_max = 2
        return player

    def _make_enemy(self, hp=20) -> Character:
        return Character(
            "Goblin", hp=hp, ac=8, attack_bonus=3,
            dmg_num=1, dmg_die=6, dmg_bonus=1,
            class_name="Fighter",
        )

    def test_goliath_fire_on_hit_queues_trigger(self):
        player = self._make_goliath_player("fire")
        state = GameState(player)
        enemy = self._make_enemy()
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (20, 21)}

        state._queue_on_hit_species_triggers(enemy)
        self.assertEqual(len(state.pending_triggers), 1)
        self.assertIn("Fire's Burn", state.pending_triggers[0]["title"])

    def test_no_species_trigger_when_no_uses(self):
        player = self._make_goliath_player("fire")
        player.giant_ancestry_uses_remaining = 0
        state = GameState(player)
        enemy = self._make_enemy()

        state._queue_on_hit_species_triggers(enemy)
        self.assertEqual(len(state.pending_triggers), 0)


class TestTriggerPhaseTransitions(unittest.TestCase):
    """Phase transitions between player_input, processing, and awaiting_trigger."""

    def _make_state(self) -> GameState:
        player = Character(
            "Hero", hp=30, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
            class_name="Fighter",
            ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
        )
        return GameState(player)

    def test_attack_with_push_mastery_enters_trigger_phase(self):
        """When an attack hits with Push mastery, game should enter awaiting_trigger."""
        state = self._make_state()
        weapon = WEAPONS.get("Greatclub")
        if weapon:
            state.player.equipped_weapon = weapon
        enemy = Character(
            "Goblin", hp=100, ac=1, attack_bonus=1,
            dmg_num=1, dmg_die=4, dmg_bonus=0,
            class_name="Fighter",
        )
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (20, 21)}
        state.turn_phase = "player_input"
        state.player_turn_started = True

        # Force a hit by patching roll
        with patch("character.Character.roll_d20", return_value=20):
            state.attack_enemy_at((20, 21))

        # If mastery is Push, we should now be in awaiting_trigger
        mastery = state.player.get_weapon_mastery().strip().lower()
        if mastery == "push":
            self.assertEqual(state.turn_phase, "awaiting_trigger")
            self.assertTrue(len(state.pending_triggers) > 0)


if __name__ == "__main__":
    unittest.main()
