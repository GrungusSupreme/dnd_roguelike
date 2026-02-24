import unittest
import character
import dice


class TestCombat(unittest.TestCase):
    def setUp(self):
        self.player = character.Character("Player", hp=20, ac=15, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=3)
        self.goblin = character.Character("Goblin", hp=12, ac=13, attack_bonus=4, dmg_num=1, dmg_die=6)
        self._orig_roll_die = dice.roll_die
        self._orig_roll_dice = dice.roll_dice

    def tearDown(self):
        dice.roll_die = self._orig_roll_die
        dice.roll_dice = self._orig_roll_dice

    def test_natural_20_crit_hits_and_applies_extra_damage(self):
        dice.roll_die = lambda sides=20: 20
        dice.roll_dice = lambda num, sides: 3
        self.player.attack(self.goblin)
        expected_dmg = 3 + 3 + self.player.dmg_bonus
        self.assertEqual(self.goblin.hp, 12 - expected_dmg)

    def test_hit_reduces_hp(self):
        dice.roll_die = lambda sides=20: 10
        dice.roll_dice = lambda num, sides: 4
        self.player.attack(self.goblin)
        expected = 12 - (4 + self.player.dmg_bonus)
        self.assertEqual(self.goblin.hp, expected)

    def test_miss_does_not_reduce_hp(self):
        dice.roll_die = lambda sides=20: 1
        dice.roll_dice = lambda num, sides: 100
        self.player.attack(self.goblin)
        self.assertEqual(self.goblin.hp, 12)

    def test_initiative_ordering(self):
        # deterministic initiative: player rolls 10, goblin1 8, goblin2 5
        seq = iter([10, 8, 5])
        dice.roll_die = lambda *a, **k: next(seq)
        player = character.Character("Player", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, initiative_bonus=0)
        g1 = character.Character("G1", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, initiative_bonus=0)
        g2 = character.Character("G2", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, initiative_bonus=0)
        # roll_initiative returns (total, raw_roll)
        player_init = player.roll_initiative()[0]
        g1_init = g1.roll_initiative()[0]
        g2_init = g2.roll_initiative()[0]
        self.assertTrue(player_init > g1_init > g2_init)

    def test_initiative_tiebreak(self):
        # two actors tie on initial total; tie-breaker should order by extra d20 roll
        # Sequence: initial rolls -> player 10, g1 10 ; tie-break rolls -> player 15, g1 3
        seq = iter([10, 10, 15, 3])
        dice.roll_die = lambda *a, **k: next(seq)
        player = character.Character("Player", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, initiative_bonus=0)
        g1 = character.Character("G1", hp=1, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1, initiative_bonus=0)
        # build initial tuples (actor, total, raw, is_player)
        p_total, p_raw = player.roll_initiative()
        g_total, g_raw = g1.roll_initiative()
        ordered = __import__("main").compute_initiative_order([
            (player, p_total, p_raw, True), (g1, g_total, g_raw, False)
        ])
        # after tie-break, player should come before g1
        self.assertEqual(ordered[0][0].name, "Player")

    def test_ranged_in_melee_shows_disadvantage_note(self):
        archer = character.Character("Archer", hp=20, ac=15, attack_bonus=5, dmg_num=1, dmg_die=8, dmg_bonus=3, attack_range=3)
        target = character.Character("Target", hp=12, ac=15, attack_bonus=4, dmg_num=1, dmg_die=6)
        seq = iter([18, 5])
        dice.roll_die = lambda sides=20: next(seq)
        dice.roll_dice = lambda num, sides: 4

        result = archer.attack(target, target_distance=1)

        self.assertIn("Disadvantage: Ranged in melee", result)


if __name__ == "__main__":
    unittest.main()
