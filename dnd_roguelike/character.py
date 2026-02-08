"""Character model and combat actions."""
import dice


class Character:
    def __init__(self, name, hp, ac, attack_bonus, dmg_num, dmg_die, dmg_bonus=0, initiative_bonus=0, potions=0, bounty=0, behavior=None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.ac = ac
        self.attack_bonus = attack_bonus
        self.dmg_num = dmg_num
        self.dmg_die = dmg_die
        self.dmg_bonus = dmg_bonus
        self.initiative_bonus = initiative_bonus
        self.potions = potions
        self.temp_ac_bonus = 0
        self.gold = 0
        self.bounty = bounty
        self.behavior = behavior
        self.inventory = []

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        roll = dice.roll_die()
        total = roll + self.attack_bonus
        effective_ac = target.ac + getattr(target, "temp_ac_bonus", 0)
        hit = (roll == 20) or (total >= effective_ac)
        if hit:
            dmg = dice.roll_dice(self.dmg_num, self.dmg_die) + self.dmg_bonus
            if roll == 20:
                dmg += dice.roll_dice(self.dmg_num, self.dmg_die)
            target.hp -= dmg
            target_hp = max(target.hp, 0)
            print(f"{self.name} rolls {roll}+{self.attack_bonus} = {total} vs AC {target.ac} -> HIT for {dmg} dmg (target HP {target_hp})")
        else:
            print(f"{self.name} rolls {roll}+{self.attack_bonus} = {total} vs AC {target.ac} -> MISS")

    def roll_initiative(self):
        """Roll initiative (d20 + initiative bonus).

        Returns a tuple `(total, roll)` where `total` is the final initiative
        (roll + initiative_bonus) and `roll` is the raw d20 roll. Returning the
        raw roll helps tie-breaking logic remain deterministic in tests.
        """
        roll = dice.roll_die()
        total = roll + self.initiative_bonus
        return total, roll

    def heal(self, amount):
        """Heal the character up to max_hp."""
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def use_potion(self, amount):
        """Consume a potion to heal. Returns healed amount or 0 if none."""
        if self.potions <= 0:
            return 0
        self.potions -= 1
        return self.heal(amount)

    def add_item(self, item):
        """Add an Item to inventory and apply immediate effects (e.g., potion count)."""
        self.inventory.append(item)
        if getattr(item, "kind", None) == "potion":
            self.potions += 1
        return item

    # Leveling / XP
    xp: int = 0
    level: int = 1

    def xp_to_next_level(self):
        """Simple XP curve: 100 * current level."""
        return 100 * self.level

    def add_xp(self, amount):
        """Add XP and level up if threshold reached. Returns number of levels gained."""
        if amount <= 0:
            return 0
        self.xp += amount
        levels_gained = 0
        while self.xp >= self.xp_to_next_level():
            self.xp -= self.xp_to_next_level()
            self.level_up()
            levels_gained += 1
        return levels_gained

    def level_up(self):
        """Increase level and improve stats. Simple growth: +5 max HP, +1 attack every level, +1 AC every 2 levels."""
        self.level += 1
        self.max_hp += 5
        # heal some on level up
        self.hp = min(self.max_hp, self.hp + 5)
        self.attack_bonus += 1
        if self.level % 2 == 0:
            self.ac += 1

    def defend(self, ac_bonus=2):
        """Apply a temporary AC bonus for the rest of the round."""
        self.temp_ac_bonus = ac_bonus

    def heal_ally(self, target, amount):
        """Heal an allied character by consuming a potion if available.

        Returns the healed amount (0 if no potion available).
        """
        if self.potions <= 0:
            return 0
        self.potions -= 1
        return target.heal(amount)
