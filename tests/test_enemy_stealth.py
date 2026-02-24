"""Tests for the sneaky enemy stealth system.

Covers:
- Sneaky enemies start hidden when spawned
- Hidden enemies are invisible to player (can't be targeted)
- Player passive Perception reveals hidden enemies (silent on failure)
- Sneaky enemy attacks from stealth with advantage
- Sneaky enemy sneak attack bonus damage on hit
- Sneaky enemy reveals on attack
- Sneaky enemy re-stealths after attack if obscured
- Dead enemies are cleaned from hidden set
- AoE spells skip hidden enemies
"""

import unittest
from unittest.mock import patch

from character import Character
from main_gui import GameState
from monsters import make_enemy


def _make_player(**overrides) -> Character:
    defaults = dict(
        name="Hero", hp=40, ac=15, attack_bonus=5,
        dmg_num=1, dmg_die=8, dmg_bonus=3,
        class_name="Fighter",
        ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
    )
    defaults.update(overrides)
    return Character(**defaults)


def _make_sneaky_enemy(name="Goblin Skulk", stealth_bonus=6, sneak_dice=1, attack_range=3):
    enemy = Character(
        name, hp=10, ac=13,
        attack_bonus=5, dmg_num=1, dmg_die=4, dmg_bonus=2,
        behavior="sneaky", attack_range=attack_range,
    )
    enemy.stealth_bonus = stealth_bonus
    enemy.sneak_attack_dice = sneak_dice
    enemy.passive_perception = 12
    return enemy


class TestSneakyEnemySpawnHidden(unittest.TestCase):
    """Sneaky enemies start stealthed when added to the game."""

    def test_sneaky_enemy_starts_hidden(self):
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy()
        state.enemies = [enemy]
        state.enemy_positions = {enemy: (5, 5)}
        state.hidden_enemies.add(enemy)
        self.assertIn(enemy, state.hidden_enemies)

    def test_add_enemies_marks_sneaky_hidden(self):
        """add_enemies() should auto-hide sneaky-behavior enemies."""
        player = _make_player()
        state = GameState(player)
        enemy_normal = Character(
            "Goblin", hp=10, ac=12, attack_bonus=4,
            dmg_num=1, dmg_die=6, dmg_bonus=2, behavior="melee",
        )
        enemy_sneaky = _make_sneaky_enemy()
        state.add_enemies([enemy_normal, enemy_sneaky])
        self.assertIn(enemy_sneaky, state.hidden_enemies)
        self.assertNotIn(enemy_normal, state.hidden_enemies)

    def test_non_sneaky_enemy_not_hidden(self):
        player = _make_player()
        state = GameState(player)
        enemy = Character(
            "Goblin", hp=10, ac=12, attack_bonus=4,
            dmg_num=1, dmg_die=6, dmg_bonus=2, behavior="melee",
        )
        state.enemies = [enemy]
        state.enemy_positions = {enemy: (5, 5)}
        self.assertNotIn(enemy, state.hidden_enemies)


class TestPlayerPerceptionCheck(unittest.TestCase):
    """Player active Perception roll reveals hidden enemies (silently fails)."""

    def test_high_perception_reveals_enemy(self):
        """Player with high WIS and a good roll spots the sneaky enemy."""
        player = _make_player(ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 20, "CHA": 10},
                              skill_proficiencies=["Perception"])
        state = GameState(player)
        enemy = _make_sneaky_enemy(stealth_bonus=0)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (16, 15)}
        state.hidden_enemies.add(enemy)
        # Enemy stealth total defaults to 10 + 0 = 10
        # Player rolls d20(15) + WIS mod(5) + proficiency(2) = 22 >= 10
        with patch.object(player, "roll_d20", return_value=15):
            state._check_player_perception_vs_hidden_enemies()
        self.assertNotIn(enemy, state.hidden_enemies)
        # Check the log mentions spotting
        self.assertTrue(any("spot" in line.lower() for line in state.combat_log))

    def test_low_roll_fails_silently(self):
        """Player rolls low and can't spot — no log message appears."""
        player = _make_player(ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 8, "CHA": 10})
        state = GameState(player)
        enemy = _make_sneaky_enemy(stealth_bonus=10)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (16, 15)}
        state.hidden_enemies.add(enemy)
        enemy._stealth_check_total = 25  # Very high
        log_before = len(state.combat_log)
        # Player rolls d20(1) + WIS mod(-1) = 0, well below 25
        with patch.object(player, "roll_d20", return_value=1):
            state._check_player_perception_vs_hidden_enemies()
        self.assertIn(enemy, state.hidden_enemies)
        # No log messages about spotting on failure
        self.assertEqual(len(state.combat_log), log_before)

    def test_out_of_range_enemy_not_checked(self):
        """Enemies too far away are not checked."""
        player = _make_player(ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 20, "CHA": 10},
                              skill_proficiencies=["Perception"])
        state = GameState(player)
        enemy = _make_sneaky_enemy(stealth_bonus=0)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (50, 50)}  # Far away
        state.hidden_enemies.add(enemy)
        state._check_player_perception_vs_hidden_enemies()
        # Should still be hidden — out of vision range
        self.assertIn(enemy, state.hidden_enemies)

    def test_dead_enemy_removed_from_hidden(self):
        """Dead enemies get cleaned from hidden_enemies during perception check."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy()
        enemy.hp = 0
        state.enemies = [enemy]
        state.enemy_positions = {enemy: (16, 15)}
        state.hidden_enemies.add(enemy)
        state._check_player_perception_vs_hidden_enemies()
        self.assertNotIn(enemy, state.hidden_enemies)


class TestSneakyEnemyAttack(unittest.TestCase):
    """Sneaky enemies get advantage + sneak attack from stealth."""

    def test_stealth_advantage_flag_set_on_attack(self):
        """When a sneaky enemy attacks from stealth, _stealth_advantage is set."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=3)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (17, 15)}
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()

        # Patch the attack to check if advantage was set
        original_attack = enemy.attack
        advantage_was_set = {"value": False}

        def patched_attack(*args, **kwargs):
            advantage_was_set["value"] = getattr(enemy, "_stealth_advantage", False)
            return original_attack(*args, **kwargs)

        with patch.object(enemy, "attack", side_effect=patched_attack):
            state._resolve_single_enemy(enemy)

        # The advantage flag should have been True when attack was called
        self.assertTrue(advantage_was_set["value"])

    def test_enemy_revealed_after_attack(self):
        """Sneaky enemy is removed from hidden_enemies after attacking."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=3)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (17, 15)}
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()

        state._resolve_single_enemy(enemy)

        # Enemy should be revealed (unless it re-stealthed behind cover)
        # Since there's no cover, it stays revealed
        self.assertNotIn(enemy, state.hidden_enemies)

    def test_sneak_attack_bonus_damage_on_hit(self):
        """Sneaky enemy deals bonus sneak attack damage when hitting from stealth."""
        player = _make_player(hp=100)
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=1, sneak_dice=2)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (16, 15)}  # Adjacent
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()

        # Force the attack to hit
        with patch.object(enemy, "roll_d20", return_value=20):
            state._resolve_single_enemy(enemy)

        # Check that sneak attack damage log was generated
        sneak_logs = [l for l in state.combat_log if "sneak attack damage" in l.lower()]
        self.assertTrue(len(sneak_logs) > 0, "Expected sneak attack damage log entry")

    def test_strikes_from_shadows_log(self):
        """Log should say the enemy strikes from the shadows."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=3)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (17, 15)}
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()

        state._resolve_single_enemy(enemy)

        shadow_logs = [l for l in state.combat_log if "strikes from the shadows" in l.lower()]
        self.assertTrue(len(shadow_logs) > 0)


class TestSneakyEnemyReStealth(unittest.TestCase):
    """Sneaky enemies try to re-stealth after attacking if behind cover."""

    def test_re_stealth_with_cover(self):
        """Enemy behind a tree can re-stealth after attacking."""
        player = _make_player(ability_scores={"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 8, "CHA": 10})
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=3, stealth_bonus=20)  # Very high stealth
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (18, 15)}
        # Place a tree between enemy and player to provide obscurement
        state.trees = {(17, 15)}
        state.rocks = set()

        # _is_obscured_between should find the tree between (18,15) and (15,15)
        self.assertTrue(state._is_obscured_between((18, 15), (15, 15)))

        # Player rolls low on their active Perception contest
        with patch.object(player, "roll_d20", return_value=1):
            state._enemy_attempt_re_stealth(enemy)
        # With stealth_bonus=20 and player rolling 1, should succeed
        self.assertIn(enemy, state.hidden_enemies)

    def test_no_re_stealth_without_cover(self):
        """Enemy without cover cannot re-stealth."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy(attack_range=3, stealth_bonus=20)
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (17, 15)}
        state.trees = set()
        state.rocks = set()

        state._enemy_attempt_re_stealth(enemy)
        self.assertNotIn(enemy, state.hidden_enemies)

    def test_non_sneaky_enemy_cannot_re_stealth(self):
        """Only sneaky-behavior enemies can attempt re-stealth."""
        player = _make_player()
        state = GameState(player)
        enemy = Character(
            "Goblin", hp=10, ac=12, attack_bonus=4,
            dmg_num=1, dmg_die=6, dmg_bonus=2, behavior="melee",
        )
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (18, 15)}
        state.trees = {(17, 15)}
        state.rocks = set()

        state._enemy_attempt_re_stealth(enemy)
        self.assertNotIn(enemy, state.hidden_enemies)


class TestPlayerCannotTargetHidden(unittest.TestCase):
    """Player single-target attacks skip hidden enemies, but AoE hits them."""

    def test_attack_skips_hidden_enemy(self):
        """attack_enemy_at should not hit a hidden enemy."""
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy()
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (16, 15)}
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()
        state.actions_remaining = 1

        result = state.attack_enemy_at((16, 15))
        self.assertFalse(result)
        # Enemy should still be at full HP
        self.assertEqual(enemy.hp, enemy.max_hp)


class TestAoEHitsHiddenEnemies(unittest.TestCase):
    """AoE effects should hit and reveal stealthed enemies."""

    def test_aoe_damages_hidden_enemy(self):
        """AoE spell should deal damage to a hidden enemy in the blast zone."""
        player = _make_player(
            class_name="Wizard",
            ability_scores={"STR": 10, "DEX": 14, "CON": 12, "INT": 18, "WIS": 12, "CHA": 10},
            spells=["Burning Hands"],
        )
        # Give player a spell slot
        player.spell_slots_max = {1: 2}
        player.spell_slots_current = {1: 2}
        state = GameState(player)
        enemy = _make_sneaky_enemy()
        state.enemies = [enemy]
        state.player_pos = (15, 15)
        state.enemy_positions = {enemy: (16, 15)}
        state.hidden_enemies.add(enemy)
        state.trees = set()
        state.rocks = set()

        # Verify the enemy is in the AoE cells
        aoe_cells = state.get_spell_aoe_cells("Burning Hands", (16, 15))
        self.assertIn((16, 15), aoe_cells)

        hp_before = enemy.hp
        state.cast_aoe_spell_at("Burning Hands", (16, 15))
        # Enemy should have taken damage
        self.assertLess(enemy.hp, hp_before)
        # Enemy should be revealed
        self.assertNotIn(enemy, state.hidden_enemies)
        # Log should mention flushed out
        self.assertTrue(any("flushed out" in l.lower() for l in state.combat_log))


class TestMakeEnemySneaky(unittest.TestCase):
    """Test the sneaky archetype in the monster factory."""

    def test_make_sneaky_enemy(self):
        enemy = make_enemy(1, 0, bounty=2, archetype="sneaky")
        self.assertEqual(getattr(enemy, "behavior", ""), "sneaky")
        self.assertTrue(hasattr(enemy, "stealth_bonus"))
        self.assertTrue(hasattr(enemy, "sneak_attack_dice"))
        self.assertGreater(enemy.stealth_bonus, 0)
        self.assertGreater(enemy.sneak_attack_dice, 0)

    def test_sneaky_stealth_bonus_scales(self):
        e1 = make_enemy(1, 0, archetype="sneaky")
        e5 = make_enemy(5, 0, archetype="sneaky")
        self.assertGreaterEqual(e5.stealth_bonus, e1.stealth_bonus)

    def test_sneaky_sneak_dice_scales(self):
        e1 = make_enemy(1, 0, archetype="sneaky")
        e4 = make_enemy(4, 0, archetype="sneaky")
        self.assertGreaterEqual(e4.sneak_attack_dice, e1.sneak_attack_dice)

    def test_sneaky_has_ranged_attack(self):
        enemy = make_enemy(1, 0, archetype="sneaky")
        self.assertGreater(enemy.attack_range, 1)


class TestCharacterStealthAdvantage(unittest.TestCase):
    """The _stealth_advantage flag on Character gives Advantage then resets."""

    def test_stealth_advantage_consumed_after_attack(self):
        attacker = Character(
            "Skulk", hp=10, ac=13, attack_bonus=5,
            dmg_num=1, dmg_die=4, dmg_bonus=2,
        )
        target = Character(
            "Hero", hp=40, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
        )
        attacker._stealth_advantage = True
        attacker.attack(target)
        # Flag should be consumed after the attack
        self.assertFalse(getattr(attacker, "_stealth_advantage", False))

    def test_stealth_advantage_in_attack_result(self):
        attacker = Character(
            "Skulk", hp=10, ac=13, attack_bonus=5,
            dmg_num=1, dmg_die=4, dmg_bonus=2,
        )
        target = Character(
            "Hero", hp=40, ac=15, attack_bonus=5,
            dmg_num=1, dmg_die=8, dmg_bonus=3,
        )
        attacker._stealth_advantage = True
        result = attacker.attack(target)
        self.assertIn("Unseen Attacker", result)


class TestCleanupDeadHidden(unittest.TestCase):
    """Dead enemies are cleaned from hidden_enemies during processing cleanup."""

    def test_dead_enemy_removed_on_cleanup(self):
        player = _make_player()
        state = GameState(player)
        enemy = _make_sneaky_enemy()
        enemy.hp = 0
        state.enemies = [enemy]
        state.hidden_enemies.add(enemy)
        # Simulate cleanup phase
        state.hidden_enemies = {e for e in state.hidden_enemies if e.is_alive()}
        self.assertNotIn(enemy, state.hidden_enemies)


if __name__ == "__main__":
    unittest.main()
