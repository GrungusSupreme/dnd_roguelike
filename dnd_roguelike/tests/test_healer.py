import unittest
import character


class TestHealer(unittest.TestCase):
    def test_heal_ally_consumes_potion_and_restores_hp(self):
        healer = character.Character("Shaman", hp=6, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4, potions=1, behavior='healer')
        ally = character.Character("Ally", hp=10, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1)
        ally.hp = 3  # injured
        healed = healer.heal_ally(ally, 6)
        self.assertEqual(healed, 6)
        self.assertEqual(ally.hp, 9)
        self.assertEqual(healer.potions, 0)

    def test_heal_ally_no_potion_returns_zero(self):
        healer = character.Character("Shaman", hp=6, ac=10, attack_bonus=0, dmg_num=1, dmg_die=4, potions=0, behavior='healer')
        ally = character.Character("Ally", hp=10, ac=10, attack_bonus=0, dmg_num=1, dmg_die=1)
        ally.hp = 3
        healed = healer.heal_ally(ally, 6)
        self.assertEqual(healed, 0)
        self.assertEqual(ally.hp, 3)


if __name__ == "__main__":
    unittest.main()
