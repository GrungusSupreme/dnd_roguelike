"""Tests for fog of war, vision, and raid direction systems."""
import random
import unittest

from character import Character
from main_gui import GameState
from gui import GRID_WIDTH, GRID_HEIGHT, KEEP_START_X, KEEP_START_Y, KEEP_SIZE


def _make_player(**overrides) -> Character:
    defaults = dict(
        name="TestPlayer",
        hp=20,
        ac=14,
        attack_bonus=5,
        dmg_num=1,
        dmg_die=8,
        class_name="Fighter",
        ability_scores={"STR": 16, "DEX": 14, "CON": 14, "INT": 10, "WIS": 12, "CHA": 10},
    )
    defaults.update(overrides)
    return Character(**defaults)


def _make_enemy(name: str = "Goblin", hp: int = 7) -> Character:
    return Character(name, hp=hp, ac=12, attack_bonus=3, dmg_num=1, dmg_die=6)


class TestPlayerVisionRange(unittest.TestCase):
    """Verify vision range calculation based on perception + darkvision."""

    def test_base_vision_no_darkvision(self):
        """Human-like character with no darkvision gets base + perception."""
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        vision = state._player_vision_range()
        # base 10 + perception skill bonus (WIS 12 -> +1)
        self.assertGreaterEqual(vision, 10)
        # Should not exceed base + perception (no darkvision)
        self.assertLessEqual(vision, 20)

    def test_darkvision_extends_range(self):
        """Darkvision should add darkvision_range / 5 cells."""
        player_no_dv = _make_player()
        player_no_dv.darkvision_range = 0
        player_dv = _make_player()
        player_dv.darkvision_range = 60
        state_no = GameState(player_no_dv)
        state_dv = GameState(player_dv)
        self.assertEqual(
            state_dv._player_vision_range() - state_no._player_vision_range(),
            12,  # 60 / 5
        )

    def test_high_darkvision(self):
        """120 ft darkvision should add 24 cells."""
        player = _make_player()
        player.darkvision_range = 120
        state = GameState(player)
        # base 10 + perception + 24
        self.assertGreaterEqual(state._player_vision_range(), 34)


class TestVisibilityComputation(unittest.TestCase):
    """Verify compute_player_visibility produces sensible output."""

    def test_player_pos_always_visible(self):
        player = _make_player()
        state = GameState(player)
        visible = state.compute_player_visibility()
        self.assertIn(state.player_pos, visible)

    def test_adjacent_cells_visible(self):
        player = _make_player()
        state = GameState(player)
        px, py = state.player_pos
        visible = state.compute_player_visibility()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = px + dx, py + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    self.assertIn((nx, ny), visible, f"({nx}, {ny}) should be visible")

    def test_far_away_cell_not_visible(self):
        """A cell beyond vision range should not be visible."""
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        state.player_pos = (32, 32)
        visible = state.compute_player_visibility()
        vision = state._player_vision_range()
        # Cell far beyond range
        far_cell = (32, 32 + vision + 5)
        if far_cell[1] < GRID_HEIGHT:
            self.assertNotIn(far_cell, visible)

    def test_rock_blocks_los(self):
        """A rock between player and target should block line of sight."""
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        state.player_pos = (32, 32)
        state.rocks = {(32, 34)}
        state.obstacles = set(state.rocks)
        visible = state.compute_player_visibility()
        # Cell directly behind rock should be blocked
        self.assertNotIn((32, 36), visible)

    def test_is_cell_visible_lazy_recompute(self):
        """Setting player_pos directly should trigger lazy recomputation."""
        player = _make_player()
        state = GameState(player)
        state.player_pos = (10, 10)
        # The cache is now stale; is_cell_visible should recompute
        self.assertTrue(state.is_cell_visible(10, 10))
        self.assertTrue(state.is_cell_visible(11, 10))

    def test_visibility_updates_on_move(self):
        """move_player should recompute visibility."""
        player = _make_player()
        state = GameState(player)
        state.player_pos = (30, 30)
        state.compute_player_visibility()
        old_visible = set(state._visible_cells)
        state.movement_max = 100
        state.move_player(35, 35)
        new_visible = set(state._visible_cells)
        # The sets should not be identical – player moved
        self.assertNotEqual(old_visible, new_visible)


class TestRaidDirectionSpawning(unittest.TestCase):
    """Verify enemies spawn from 1-3 sides, never all 4."""

    def test_raid_sides_between_1_and_3(self):
        player = _make_player()
        for seed in range(50):
            random.seed(seed)
            state = GameState(player)
            enemies = [_make_enemy(f"G{i}") for i in range(4)]
            state.add_enemies(enemies)
            self.assertGreaterEqual(len(state.raid_sides), 1)
            self.assertLessEqual(len(state.raid_sides), 3)

    def test_at_least_one_side_free(self):
        player = _make_player()
        for seed in range(50):
            random.seed(seed)
            state = GameState(player)
            enemies = [_make_enemy(f"G{i}") for i in range(6)]
            state.add_enemies(enemies)
            all_sides = {"north", "south", "east", "west"}
            free = all_sides - set(state.raid_sides)
            self.assertTrue(len(free) >= 1, f"Seed {seed}: no free side!")

    def test_enemies_spawn_on_correct_edges(self):
        """All enemies should be placed along the edges of their raid sides."""
        player = _make_player()
        random.seed(42)
        state = GameState(player)
        enemies = [_make_enemy(f"G{i}") for i in range(5)]
        state.add_enemies(enemies)

        edge_depth = 3
        for enemy, pos in state.enemy_positions.items():
            x, y = pos
            on_valid_edge = False
            for side in state.raid_sides:
                if side == "north" and y < edge_depth:
                    on_valid_edge = True
                elif side == "south" and y >= GRID_HEIGHT - edge_depth:
                    on_valid_edge = True
                elif side == "east" and x >= GRID_WIDTH - edge_depth:
                    on_valid_edge = True
                elif side == "west" and x < edge_depth:
                    on_valid_edge = True
            self.assertTrue(
                on_valid_edge,
                f"{enemy.name} at {pos} not on any raid edge {state.raid_sides}",
            )

    def test_enemies_not_in_keep(self):
        player = _make_player()
        for seed in range(10):
            random.seed(seed)
            state = GameState(player)
            enemies = [_make_enemy(f"G{i}") for i in range(5)]
            state.add_enemies(enemies)
            for enemy, pos in state.enemy_positions.items():
                x, y = pos
                in_keep = (
                    KEEP_START_X <= x < KEEP_START_X + KEEP_SIZE
                    and KEEP_START_Y <= y < KEEP_START_Y + KEEP_SIZE
                )
                self.assertFalse(in_keep, f"{enemy.name} spawned inside keep at {pos}")


class TestHornBlastMessage(unittest.TestCase):
    """Verify correct horn blast messaging."""

    def test_single_side_message(self):
        player = _make_player()
        state = GameState(player)
        state.raid_sides = ["north"]
        msg = state._generate_horn_blast_message()
        self.assertIn("North", msg)
        self.assertIn("War horns", msg)

    def test_two_sides_message(self):
        player = _make_player()
        state = GameState(player)
        state.raid_sides = ["north", "east"]
        msg = state._generate_horn_blast_message()
        self.assertIn("North", msg)
        self.assertIn("East", msg)
        self.assertIn(" and ", msg)

    def test_three_sides_message(self):
        player = _make_player()
        state = GameState(player)
        state.raid_sides = ["north", "south", "west"]
        msg = state._generate_horn_blast_message()
        self.assertIn("North", msg)
        self.assertIn("South", msg)
        self.assertIn("West", msg)


class TestLighting(unittest.TestCase):
    """Verify the night-raid lighting zones."""

    def test_keep_interior_is_lit(self):
        """Cells inside the keep should be well-lit."""
        player = _make_player()
        state = GameState(player)
        cx = KEEP_START_X + KEEP_SIZE // 2
        cy = KEEP_START_Y + KEEP_SIZE // 2
        self.assertTrue(state.is_cell_lit(cx, cy))

    def test_clearing_is_lit(self):
        """Cells in the clearing ring around the keep should be lit."""
        player = _make_player()
        state = GameState(player)
        # 3 cells outside keep wall – well within LIGHT_RADIUS (6)
        x = KEEP_START_X - 3
        y = KEEP_START_Y + KEEP_SIZE // 2
        self.assertTrue(state.is_cell_lit(x, y))

    def test_forest_is_unlit(self):
        """Cells far from the keep in the forest should be dark."""
        player = _make_player()
        state = GameState(player)
        self.assertFalse(state.is_cell_lit(0, 0))
        self.assertFalse(state.is_cell_lit(5, 5))
        self.assertFalse(state.is_cell_lit(60, 60))

    def test_get_lit_cells_returns_set(self):
        player = _make_player()
        state = GameState(player)
        lit = state.get_lit_cells()
        self.assertIsInstance(lit, set)
        self.assertTrue(len(lit) > 0)
        # Every cell in the set should pass is_cell_lit
        for x, y in list(lit)[:20]:
            self.assertTrue(state.is_cell_lit(x, y))

    def test_get_lit_cells_cached(self):
        player = _make_player()
        state = GameState(player)
        a = state.get_lit_cells()
        b = state.get_lit_cells()
        self.assertIs(a, b)


class TestTreeBlocksLOS(unittest.TestCase):
    """Verify that ~50% of trees block line of sight."""

    def test_tree_blocks_los_deterministic(self):
        """_tree_blocks_los should return the same value for a given position."""
        player = _make_player()
        state = GameState(player)
        for x in range(10):
            for y in range(10):
                a = state._tree_blocks_los(x, y)
                b = state._tree_blocks_los(x, y)
                self.assertEqual(a, b)

    def test_roughly_half_trees_block(self):
        """Across many positions, roughly half should block."""
        blocking = sum(
            1 for x in range(100) for y in range(100)
            if GameState._tree_blocks_los(x, y)
        )
        total = 100 * 100
        ratio = blocking / total
        self.assertGreater(ratio, 0.3)
        self.assertLess(ratio, 0.7)

    def test_dense_tree_blocks_los_ray(self):
        """A dense (blocking) tree should stop LOS through it."""
        player = _make_player()
        state = GameState(player)
        # Place player in keep (lit) and find a tree position that blocks
        state.player_pos = (32, 32)
        # Find a coordinate where _tree_blocks_los is True
        for ty in range(33, 40):
            if state._tree_blocks_los(32, ty):
                state.trees = {(32, ty)}
                state.rocks = set()
                visible = state.compute_player_visibility()
                # Cell behind the blocking tree should not be visible
                behind = (32, ty + 2)
                if behind[1] < GRID_HEIGHT and state.is_cell_lit(*behind):
                    self.assertNotIn(behind, visible,
                                     f"Cell behind dense tree at (32,{ty}) should be hidden")
                break

    def test_sparse_tree_does_not_block_los(self):
        """A sparse (non-blocking) tree should not stop LOS."""
        player = _make_player()
        state = GameState(player)
        state.player_pos = (32, 32)
        # Find a coordinate where _tree_blocks_los is False
        for ty in range(33, 40):
            if not state._tree_blocks_los(32, ty):
                state.trees = {(32, ty)}
                state.rocks = set()
                visible = state.compute_player_visibility()
                # Cell behind the non-blocking tree should be visible
                behind = (32, ty + 2)
                if behind[1] < GRID_HEIGHT and state.is_cell_lit(*behind):
                    self.assertIn(behind, visible,
                                  f"Cell behind sparse tree at (32,{ty}) should be visible")
                break


class TestDarknessVisibility(unittest.TestCase):
    """Verify that darkness limits visibility for non-darkvision characters."""

    def test_no_darkvision_limited_in_dark(self):
        """Without darkvision, vision into dark cells is very short."""
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        # Put player in the dark forest
        state.player_pos = (5, 5)
        state.rocks = set()
        state.trees = set()
        visible = state.compute_player_visibility()
        dark_range = state._player_dark_vision_range()
        # Cells beyond DARK_VISION_MIN in the dark should not be visible
        far_dark = (5, 5 + dark_range + 3)
        if far_dark[1] < GRID_HEIGHT and not state.is_cell_lit(*far_dark):
            self.assertNotIn(far_dark, visible)

    def test_darkvision_sees_further_in_dark(self):
        """With darkvision, vision into dark areas extends much further."""
        player = _make_player()
        player.darkvision_range = 60  # 12 cells
        state = GameState(player)
        state.player_pos = (5, 5)
        state.rocks = set()
        state.trees = set()
        visible = state.compute_player_visibility()
        # A cell 8 cells away in the dark should be visible with darkvision
        target = (5, 13)
        self.assertFalse(state.is_cell_lit(*target))
        self.assertIn(target, visible)

    def test_dark_vision_range_without_darkvision(self):
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        self.assertEqual(state._player_dark_vision_range(), state.DARK_VISION_MIN)

    def test_dark_vision_range_with_darkvision(self):
        player = _make_player()
        player.darkvision_range = 60
        state = GameState(player)
        self.assertEqual(state._player_dark_vision_range(), 12)

    def test_lit_area_full_vision(self):
        """Player in lit keep should see lit cells at full range."""
        player = _make_player()
        player.darkvision_range = 0
        state = GameState(player)
        # Player in the keep centre
        state.player_pos = (KEEP_START_X + KEEP_SIZE // 2, KEEP_START_Y + KEEP_SIZE // 2)
        state.rocks = set()
        state.trees = set()
        visible = state.compute_player_visibility()
        # A lit cell 5 cells away in the clearing should be visible
        target = (KEEP_START_X + KEEP_SIZE // 2, KEEP_START_Y + KEEP_SIZE + 3)
        self.assertTrue(state.is_cell_lit(*target))
        self.assertIn(target, visible)


class TestFogOfWarTargeting(unittest.TestCase):
    """Verify players cannot target enemies hidden in the fog."""

    def test_cannot_attack_fogged_enemy(self):
        player = _make_player()
        state = GameState(player)
        enemy = _make_enemy()
        state.enemies = [enemy]
        # Place player and enemy far apart – enemy should be in fog
        state.player_pos = (5, 5)
        state.enemy_positions = {enemy: (60, 60)}
        state.rocks = set()
        state.trees = set()
        state.actions_remaining = 1
        result = state.attack_enemy_at((60, 60))
        self.assertFalse(result)
        self.assertIn("can't see", state.message)

    def test_can_attack_visible_enemy(self):
        player = _make_player()
        state = GameState(player)
        enemy = _make_enemy()
        enemy.ac = 5  # easy to hit
        state.enemies = [enemy]
        state.player_pos = (20, 20)
        state.enemy_positions = {enemy: (21, 20)}
        state.rocks = set()
        state.trees = set()
        state.actions_remaining = 1
        player.roll_d20 = lambda: 20
        result = state.attack_enemy_at((21, 20))
        self.assertTrue(result)

    def test_cannot_cast_at_fogged_position(self):
        player = _make_player(class_name="Wizard", spells=["Fire Bolt"])
        state = GameState(player)
        enemy = _make_enemy()
        state.enemies = [enemy]
        state.player_pos = (5, 5)
        state.enemy_positions = {enemy: (60, 60)}
        state.rocks = set()
        state.trees = set()
        result = state.cast_spell_at("Fire Bolt", (60, 60))
        self.assertFalse(result)
        self.assertIn("can't see", state.message)

    def test_self_aoe_ignores_fog(self):
        """Self-centred AoE like Thunderwave should work regardless of fog."""
        player = _make_player(class_name="Wizard", spells=["Thunderwave"])
        state = GameState(player)
        state.enemies = []
        state.player_pos = (20, 20)
        state.enemy_positions = {}
        state.rocks = set()
        state.trees = set()
        acted = state.cast_aoe_spell_at("Thunderwave", (20, 20))
        self.assertTrue(acted)


if __name__ == "__main__":
    unittest.main()
