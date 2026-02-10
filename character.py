"""Character model and combat actions."""
import dice
from class_features import get_class_features


class Character:
    def __init__(self, name, hp, ac, attack_bonus, dmg_num, dmg_die, dmg_bonus=0, initiative_bonus=0, potions=0, bounty=0, behavior=None, class_name=None, ability_scores=None):
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
        self.class_name = class_name or "Hero"
        self.features = get_class_features(self.class_name)
        
        # Ability scores (STR, DEX, CON, INT, WIS, CHA)
        # If not provided, defaults to standard physical scores
        if ability_scores is None:
            ability_scores = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        self.ability_scores = ability_scores

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
    def use_feature(self, feature_name):
        """Use a class feature if available.
        
        Args:
            feature_name: Name of the feature to use (e.g., "Rage").
            
        Returns:
            True if feature was available and used, False otherwise.
        """
        for feature in self.features:
            if feature.name == feature_name:
                return feature.use()
        return False
    
    def get_feature(self, feature_name):
        """Get a feature by name.
        
        Args:
            feature_name: Name of the feature.
            
        Returns:
            ClassFeature object or None if not found.
        """
        for feature in self.features:
            if feature.name == feature_name:
                return feature
        return None
    
    def get_available_features(self):
        """Get list of features that have uses remaining.
        
        Returns:
            List of available ClassFeature objects.
        """
        return [f for f in self.features if f.uses_remaining > 0 or f.max_uses is None]
    
    def rest_features(self):
        """Restore all features on a long rest (typically between waves)."""
        for feature in self.features:
            if feature.recharge == "rest":
                feature.restore()
    
    def display_features(self):
        """Return a formatted string of all class features.
        
        Returns:
            Multi-line string showing feature names and usage.
        """
        if not self.features:
            return "No class features."
        lines = []
        for feature in self.features:
            if feature.max_uses is None:
                status = "[Always available]"
            else:
                status = f"[{feature.uses_remaining}/{feature.max_uses} uses]"
            lines.append(f"  {feature.name}: {status}")
        return "\n".join(lines)
    
    def get_ability_modifier(self, ability: str) -> int:
        """Calculate ability modifier from ability score.
        
        Args:
            ability: Ability name (STR, DEX, CON, INT, WIS, CHA)
            
        Returns:
            Ability modifier (formula: (score - 10) // 2)
        """
        score = self.ability_scores.get(ability, 10)
        return (score - 10) // 2
    
    def get_all_modifiers(self) -> dict:
        """Get modifiers for all abilities.
        
        Returns:
            Dict with ability names as keys and modifiers as values.
        """
        return {ability: self.get_ability_modifier(ability) 
                for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}