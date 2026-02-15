"""Character model and combat actions."""
import dice
from class_features import get_class_features
from spell_data import (
    get_spell_slots_max,
    get_spell_definition,
    get_spellcasting_requirements,
    is_spellcaster_class,
)


class Character:
    def __init__(
        self,
        name,
        hp,
        ac,
        attack_bonus,
        dmg_num,
        dmg_die,
        dmg_bonus=0,
        initiative_bonus=0,
        potions=0,
        bounty=0,
        behavior=None,
        class_name=None,
        ability_scores=None,
        attack_range=1,
        background=None,
        skill_proficiencies=None,
        spells=None,
        species=None,
        species_traits=None,
        origin_feats=None,
        speed_ft=30,
        speed_bonus_ft=0,
        tool_proficiencies=None,
        gold=0,
        spell_slots_current=None,
        spell_slots_max=None,
    ):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.ac = ac
        self.attack_bonus = attack_bonus
        self.dmg_num = dmg_num
        self.dmg_die = dmg_die
        self.dmg_bonus = dmg_bonus
        self.initiative_bonus = initiative_bonus
        self.attack_range = attack_range
        self.potions = potions
        self.temp_ac_bonus = 0
        self.gold = gold
        self.bounty = bounty
        self.behavior = behavior
        self.inventory = []
        self.class_name = class_name or "Hero"
        self.features = get_class_features(self.class_name)
        self.raging = False
        self.rage_rounds_remaining = 0
        self.sneak_attack_used = False
        self.inspiration_die = 0
        self.lay_on_hands_pool = 0
        if self.get_feature("Lay On Hands"):
            self.lay_on_hands_pool = 5 * self.level
        
        # Ability scores (STR, DEX, CON, INT, WIS, CHA)
        # If not provided, defaults to standard physical scores
        if ability_scores is None:
            ability_scores = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        self.ability_scores = ability_scores
        self.background = background
        self.skill_proficiencies = list(skill_proficiencies or [])
        self.spells = list(spells or [])
        self.species = species
        self.species_traits = dict(species_traits or {})
        self.origin_feats = list(origin_feats or [])
        self.tool_proficiencies = list(tool_proficiencies or [])
        self.speed_ft = speed_ft
        self.speed_bonus_ft = speed_bonus_ft
        self.spell_slots_max = {}
        self.spell_slots_current = {}
        self.spellcasting_ability = "INT"
        self._initialize_spellcasting(spell_slots_current, spell_slots_max)
        self.temp_hp = 0
        self.save_advantage_tags = set()
        self.halfling_lucky = False
        self.naturally_stealthy = False
        self.relentless_endurance_available = False
        self.adrenaline_rush_uses_remaining = 0
        self.adrenaline_rush_uses_max = 0
        self.stonecunning_uses_remaining = 0
        self.stonecunning_uses_max = 0
        self.tremorsense_range = 0
        self.tremorsense_rounds_remaining = 0
        self.giant_ancestry = None
        self.giant_ancestry_uses_remaining = 0
        self.giant_ancestry_uses_max = 0
        self.goliath_large_form_available = False
        self.goliath_large_form_active = False
        self.goliath_large_form_rounds_remaining = 0
        self.damage_resistances = set()
        self.darkvision_range = 0
        self.breath_weapon_damage_type = None
        self.breath_weapon_uses_max = 0
        self.breath_weapon_uses_remaining = 0
        self.species_magic = None
        self.status_effects = {}
        self._initialize_species_features()
        
        # Equipment slots
        self.equipped_weapon = None  # Weapon object
        self.equipped_armor = None  # Armor object
        self.equipped_offhand = None  # Shield or secondary weapon
        self.inventory = []  # Carried items

    def get_speed_ft(self) -> int:
        """Return current speed in feet, including bonuses."""
        return max(0, self.speed_ft + self.speed_bonus_ft)

    def _initialize_spellcasting(self, spell_slots_current=None, spell_slots_max=None):
        class_name = self.class_name or ""
        if is_spellcaster_class(class_name):
            req = get_spellcasting_requirements(class_name)
            self.spellcasting_ability = req.get("ability", "INT")
            computed_max = get_spell_slots_max(class_name, self.level)
            self.spell_slots_max = dict(spell_slots_max or computed_max)
            if spell_slots_current is None:
                self.spell_slots_current = dict(self.spell_slots_max)
            else:
                self.spell_slots_current = dict(spell_slots_current)
                for lvl, cap in self.spell_slots_max.items():
                    self.spell_slots_current[lvl] = min(cap, self.spell_slots_current.get(lvl, cap))
        else:
            self.spell_slots_max = {}
            self.spell_slots_current = {}

    def is_spellcaster(self) -> bool:
        return is_spellcaster_class(self.class_name or "")

    def get_spellcasting_modifier(self) -> int:
        return self.get_ability_modifier(self.spellcasting_ability)

    def get_spell_slots_summary(self) -> str:
        if not self.spell_slots_max:
            return ""
        parts = []
        for lvl in sorted(self.spell_slots_max.keys()):
            cur = self.spell_slots_current.get(lvl, 0)
            cap = self.spell_slots_max.get(lvl, 0)
            parts.append(f"L{lvl} {cur}/{cap}")
        return " | ".join(parts)

    def can_cast_spell(self, spell_name: str) -> bool:
        spell = get_spell_definition(spell_name)
        if not spell or spell_name not in self.spells:
            return False
        level = int(spell.get("level", 0))
        if level <= 0:
            return True
        return self.spell_slots_current.get(level, 0) > 0

    def get_combat_spells(self):
        result = []
        for spell_name in self.spells:
            spell = get_spell_definition(spell_name)
            if spell:
                result.append(spell_name)
        return result

    def get_spell_target_mode(self, spell_name: str) -> str:
        spell = get_spell_definition(spell_name)
        return str(spell.get("target", "enemy")) if spell else "enemy"

    def get_spell_range(self, spell_name: str) -> int:
        spell = get_spell_definition(spell_name)
        return int(spell.get("range", 0)) if spell else 0

    def get_spell_aoe(self, spell_name: str):
        spell = get_spell_definition(spell_name)
        aoe = spell.get("aoe") if spell else None
        return dict(aoe) if isinstance(aoe, dict) else None

    def _consume_spell_slot_if_needed(self, spell_name: str) -> bool:
        spell = get_spell_definition(spell_name)
        if not spell:
            return False
        level = int(spell.get("level", 0))
        if level <= 0:
            return True
        available = self.spell_slots_current.get(level, 0)
        if available <= 0:
            return False
        self.spell_slots_current[level] = available - 1
        return True

    def restore_spell_slots(self) -> None:
        self.spell_slots_current = dict(self.spell_slots_max)

    def roll_d20(self) -> int:
        roll = dice.roll_die()
        if self.halfling_lucky and roll == 1:
            roll = dice.roll_die()
        return roll

    def apply_status_effect(self, name: str, rounds: int, potency: int = 0) -> None:
        """Apply or refresh a status effect for a number of rounds."""
        key = (name or "").strip().lower()
        if not key or rounds <= 0:
            return
        current = self.status_effects.get(key, {"rounds": 0, "potency": 0})
        self.status_effects[key] = {
            "rounds": max(int(rounds), int(current.get("rounds", 0))),
            "potency": max(int(potency), int(current.get("potency", 0))),
        }

    def has_status_effect(self, name: str) -> bool:
        key = (name or "").strip().lower()
        return key in self.status_effects and self.status_effects[key].get("rounds", 0) > 0

    def get_status_summary(self) -> str:
        if not self.status_effects:
            return ""
        active = []
        for name, data in sorted(self.status_effects.items()):
            rounds = int(data.get("rounds", 0))
            if rounds > 0:
                active.append(f"{name.title()}({rounds})")
        return ", ".join(active)

    def get_attack_roll_penalty(self) -> int:
        penalty = 0
        if self.has_status_effect("poisoned"):
            penalty += 2
        return penalty

    def tick_status_effects(self) -> list[str]:
        expired = []
        for effect_name in list(self.status_effects.keys()):
            data = self.status_effects[effect_name]
            rounds = int(data.get("rounds", 0)) - 1
            if rounds <= 0:
                expired.append(effect_name)
                del self.status_effects[effect_name]
            else:
                data["rounds"] = rounds
                self.status_effects[effect_name] = data
        return expired

    def has_save_advantage(self, ability: str, effect_tag: str = "") -> bool:
        ability_key = (ability or "").strip().upper()
        effect_key = (effect_tag or "").strip().lower()
        if ability_key in {"INT", "WIS", "CHA"} and "mental" in self.save_advantage_tags:
            return True
        if effect_key and effect_key in self.save_advantage_tags:
            return True
        return False

    def roll_saving_throw(self, ability: str, dc: int, effect_tag: str = "") -> tuple[bool, int]:
        mod = self.get_ability_modifier(ability)
        roll = self.roll_d20()
        if self.has_save_advantage(ability, effect_tag):
            roll = max(roll, self.roll_d20())
        total = roll + mod
        return total >= dc, total

    def cast_spell(self, spell_name: str, target=None, log_fn=None) -> str:
        spell = get_spell_definition(spell_name)
        if not spell or spell_name not in self.spells:
            msg = f"{self.name} does not know {spell_name}."
            if log_fn:
                log_fn(msg)
            return msg

        if not self._consume_spell_slot_if_needed(spell_name):
            msg = f"{self.name} has no spell slots for {spell_name}."
            if log_fn:
                log_fn(msg)
            return msg

        hit_type = spell.get("hit_type", "attack")
        if hit_type == "aoe":
            msg = f"{spell_name} is an area spell and requires area targeting."
            if log_fn:
                log_fn(msg)
            return msg
        if hit_type == "heal":
            heal_dice = spell.get("heal", (1, 4))
            heal_amount = dice.roll_dice(heal_dice[0], heal_dice[1]) + max(0, self.get_spellcasting_modifier())
            heal_target = target if target is not None else self
            healed = heal_target.heal(heal_amount)
            msg = f"{self.name} casts {spell_name} and restores {healed} HP to {heal_target.name}."
            if log_fn:
                log_fn(msg)
            return msg

        enemy = target
        if enemy is None:
            msg = f"{self.name} needs a target for {spell_name}."
            if log_fn:
                log_fn(msg)
            return msg

        damage_tuple = spell.get("damage", (1, 6))
        damage_type = spell.get("damage_type", "force")
        roll = self.roll_d20()
        spell_attack_bonus = self.get_spellcasting_modifier() + self.get_proficiency_bonus() - self.get_attack_roll_penalty()
        target_ac = enemy.get_ac() if hasattr(enemy, "get_ac") else enemy.ac
        target_ac += getattr(enemy, "temp_ac_bonus", 0)

        if spell.get("hit_type") == "auto":
            hit = True
            total = roll + spell_attack_bonus
        else:
            total = roll + spell_attack_bonus
            hit = (roll == 20) or (total >= target_ac)

        if not hit:
            msg = f"{self.name} casts {spell_name}: {roll}+{spell_attack_bonus}={total} vs AC {target_ac} -> MISS"
            if log_fn:
                log_fn(msg)
            return msg

        raw_damage = dice.roll_dice(damage_tuple[0], damage_tuple[1])
        raw_damage += int(spell.get("flat_bonus", 0))
        if roll == 20 and spell.get("hit_type") != "auto":
            raw_damage += dice.roll_dice(damage_tuple[0], damage_tuple[1])

        resisted = False
        dealt = raw_damage
        if hasattr(enemy, "take_damage"):
            dealt, resisted = enemy.take_damage(raw_damage, damage_type=damage_type, source=self, log_fn=log_fn)
        else:
            enemy.hp -= raw_damage

        notes = " (resisted)" if resisted else ""
        msg = (
            f"{self.name} casts {spell_name}: {roll}+{spell_attack_bonus}={total} vs AC {target_ac} "
            f"-> HIT for {dealt} {damage_type} damage{notes} (target HP {max(enemy.hp, 0)})"
        )
        if log_fn:
            log_fn(msg)
        return msg

    def cast_aoe_spell(self, spell_name: str, targets: list, log_fn=None) -> str:
        """Cast an AoE spell against a list of targets. Consumes one slot if applicable."""
        spell = get_spell_definition(spell_name)
        if not spell or spell_name not in self.spells:
            msg = f"{self.name} does not know {spell_name}."
            if log_fn:
                log_fn(msg)
            return msg

        if spell.get("hit_type") != "aoe":
            return self.cast_spell(spell_name, target=targets[0] if targets else None, log_fn=log_fn)

        if not self._consume_spell_slot_if_needed(spell_name):
            msg = f"{self.name} has no spell slots for {spell_name}."
            if log_fn:
                log_fn(msg)
            return msg

        damage_tuple = spell.get("damage", (1, 6))
        damage_type = spell.get("damage_type", "force")
        raw_damage = dice.roll_dice(damage_tuple[0], damage_tuple[1])

        if not targets:
            msg = f"{self.name} casts {spell_name}, but it hits no enemies."
            if log_fn:
                log_fn(msg)
            return msg

        parts = []
        for enemy in targets:
            resisted = False
            dealt = raw_damage
            if hasattr(enemy, "take_damage"):
                dealt, resisted = enemy.take_damage(raw_damage, damage_type=damage_type, source=self, log_fn=log_fn)
            else:
                enemy.hp -= raw_damage
            notes = " (resisted)" if resisted else ""
            parts.append(f"{enemy.name} {dealt}{notes}")

        summary = ", ".join(parts)
        msg = f"{self.name} casts {spell_name} for {raw_damage} {damage_type} damage in an area: {summary}."
        if log_fn:
            log_fn(msg)
        return msg

    def get_dex_modifier(self) -> int:
        """Calculate DEX modifier from DEX ability score."""
        dex = self.ability_scores.get("DEX", 10)
        return (dex - 10) // 2

    def equip_weapon(self, weapon):
        """Equip a weapon."""
        if weapon:
            prev = self.equipped_weapon
            self.equipped_weapon = weapon
            if prev and prev not in self.inventory:
                self.inventory.append(prev)
            if weapon in self.inventory:
                self.inventory.remove(weapon)
            return True
        return False

    def equip_armor(self, armor):
        """Equip armor."""
        if armor:
            prev = self.equipped_armor
            self.equipped_armor = armor
            if prev and prev not in self.inventory:
                self.inventory.append(prev)
            if armor in self.inventory:
                self.inventory.remove(armor)
            return True
        return False

    def unequip_weapon(self):
        """Unequip current weapon and add to inventory."""
        if self.equipped_weapon:
            self.inventory.append(self.equipped_weapon)
            self.equipped_weapon = None
            return True
        return False

    def unequip_armor(self):
        """Unequip current armor and add to inventory."""
        if self.equipped_armor:
            self.inventory.append(self.equipped_armor)
            self.equipped_armor = None
            return True
        return False

    def get_ac(self) -> int:
        """Calculate current AC from armor and DEX modifier."""
        if self.equipped_armor:
            from items import Armor
            if isinstance(self.equipped_armor, Armor):
                ac = self.equipped_armor.ac_base
                dex_mod = self.get_dex_modifier()
                
                # Apply DEX bonus if allowed
                if self.equipped_armor.ac_bonus_dex:
                    max_dex = self.equipped_armor.max_dex
                    if max_dex is not None:
                        dex_mod = min(dex_mod, max_dex)
                    ac += dex_mod
                
                return ac + self.temp_ac_bonus
        
        # No armor: base 10 + DEX, with class-specific Unarmored Defense
        dex_mod = self.get_dex_modifier()
        class_key = (self.class_name or "").strip().lower()
        if class_key == "barbarian":
            return 10 + dex_mod + self.get_ability_modifier("CON") + self.temp_ac_bonus
        if class_key == "monk":
            return 10 + dex_mod + self.get_ability_modifier("WIS") + self.temp_ac_bonus
        return 10 + dex_mod + self.temp_ac_bonus

    def get_damage_dice(self) -> tuple[int, int]:
        """Return (dmg_num, dmg_die) from equipped weapon."""
        if self.equipped_weapon:
            from items import Weapon
            if isinstance(self.equipped_weapon, Weapon):
                return (self.equipped_weapon.dmg_num, self.equipped_weapon.dmg_die)
        
        # Default unarmed: 1d4
        return (1, 4)

    def get_damage_bonus(self) -> int:
        """Return total damage bonus from weapon + ability."""
        bonus = self.get_dex_modifier()  # Most weapons use DEX or STR (default DEX)
        
        if self.equipped_weapon:
            from items import Weapon
            if isinstance(self.equipped_weapon, Weapon):
                bonus += self.equipped_weapon.dmg_bonus
        
        return bonus

    def get_attack_range(self) -> int:
        """Return attack range from equipped weapon."""
        if self.equipped_weapon:
            from items import Weapon
            if isinstance(self.equipped_weapon, Weapon):
                return self.equipped_weapon.attack_range
        
        # Default melee: 1
        return 1

    def is_alive(self):
        return self.hp > 0

    def attack(self, target, log_fn=None):
        roll = self.roll_d20()
        inspiration_bonus = 0
        if self.inspiration_die > 0:
            inspiration_bonus = dice.roll_dice(1, self.inspiration_die)
            self.inspiration_die = 0
        attack_penalty = self.get_attack_roll_penalty()
        effective_attack_bonus = self.attack_bonus - attack_penalty
        total = roll + effective_attack_bonus + inspiration_bonus
        # Use dynamic AC calculation for target
        target_ac = target.get_ac() if hasattr(target, 'get_ac') else target.ac
        target_ac += getattr(target, "temp_ac_bonus", 0)
        hit = (roll == 20) or (total >= target_ac)
        if hit:
            # Use dynamic damage dice and bonus from equipped weapon
            dmg_num, dmg_die = self.get_damage_dice()
            dmg_bonus = self.get_damage_bonus()
            dmg = dice.roll_dice(dmg_num, dmg_die) + dmg_bonus
            if roll == 20:
                dmg += dice.roll_dice(dmg_num, dmg_die)
            extra_notes = []
            if inspiration_bonus > 0:
                extra_notes.append(f"Inspiration +{inspiration_bonus}")
            if self.raging:
                dmg += 2
                extra_notes.append("Rage +2")
            sneak_feature = self.get_feature("Sneak Attack")
            if sneak_feature and not self.sneak_attack_used:
                sneak_dice = self.get_sneak_attack_dice()
                if sneak_dice > 0:
                    sneak_dmg = dice.roll_dice(sneak_dice, 6)
                    dmg += sneak_dmg
                    self.sneak_attack_used = True
                    extra_notes.append(f"Sneak Attack +{sneak_dmg} ({sneak_dice}d6)")
            ancestry_notes = self._apply_goliath_on_hit_bonus(target)
            if ancestry_notes:
                dmg += ancestry_notes.get("extra_damage", 0)
                label = ancestry_notes.get("label")
                if label:
                    extra_notes.append(label)
            resisted = False
            if hasattr(target, "take_damage"):
                dmg, resisted = target.take_damage(dmg, damage_type="physical", source=self, log_fn=log_fn)
            else:
                target.hp -= dmg
            target_hp = max(target.hp, 0)
            notes = ""
            if extra_notes:
                notes = " (" + ", ".join(extra_notes) + ")"
            if resisted:
                notes = f"{notes} (resisted)" if notes else " (resisted)"
            msg = f"{self.name} rolls {roll}+{effective_attack_bonus} = {total} vs AC {target_ac} -> HIT for {dmg} dmg{notes} (target HP {target_hp})"
        else:
            target_ac = target.get_ac() if hasattr(target, 'get_ac') else target.ac
            msg = f"{self.name} rolls {roll}+{effective_attack_bonus} = {total} vs AC {target_ac} -> MISS"
        if log_fn:
            log_fn(msg)
        else:
            print(msg)
        return msg

    def _initialize_species_features(self) -> None:
        """Apply species-derived persistent features at character creation/load time."""
        species = (self.species or "").strip().lower()

        # Most origin species in the current rules set have baseline Darkvision.
        if species in {"dragonborn", "dwarf", "elf", "gnome", "goliath", "orc", "tiefling"}:
            self.darkvision_range = max(self.darkvision_range, 60)

        # Dragonborn: elemental resistance and Breath Weapon from Draconic Ancestry.
        if species == "dragonborn":
            ancestry = self.species_traits.get("Draconic Ancestry", "")
            dtype = self._parse_ancestry_damage_type(ancestry)
            if dtype:
                self.damage_resistances.add(dtype)
                self.breath_weapon_damage_type = dtype
            self._refresh_breath_weapon_uses()

        if species == "dwarf":
            self.damage_resistances.add("poison")
            self.save_advantage_tags.add("poison")
            self.max_hp += self.level
            self.hp += self.level
            self.stonecunning_uses_max = self.get_proficiency_bonus()
            self.stonecunning_uses_remaining = self.stonecunning_uses_max

        if species == "elf":
            self.save_advantage_tags.add("charmed")
            lineage = str(self.species_traits.get("Elven Lineage", "")).strip().lower()
            if lineage == "drow":
                self.darkvision_range = max(self.darkvision_range, 120)
            elif lineage == "wood elf":
                self.speed_bonus_ft += 5

        if species == "gnome":
            self.save_advantage_tags.add("mental")

        if species == "goliath":
            self.giant_ancestry = str(self.species_traits.get("Giant Ancestry", "")).strip().lower()
            self.giant_ancestry_uses_max = self.get_proficiency_bonus()
            self.giant_ancestry_uses_remaining = self.giant_ancestry_uses_max
            self.goliath_large_form_available = True

        if species == "halfling":
            self.halfling_lucky = True
            self.naturally_stealthy = True
            self.save_advantage_tags.add("frightened")

        if species == "human":
            self.inspiration_die = max(self.inspiration_die, 6)

        if species == "orc":
            self.darkvision_range = max(self.darkvision_range, 120)
            self.relentless_endurance_available = True
            self.adrenaline_rush_uses_max = self.get_proficiency_bonus()
            self.adrenaline_rush_uses_remaining = self.adrenaline_rush_uses_max

        # Tiefling: baseline fire resistance.
        if species == "tiefling":
            self.damage_resistances.add("fire")

        self._initialize_species_magic()

    def _initialize_species_magic(self) -> None:
        """Set up lightweight lineage/legacy magic actions for species traits."""
        species = (self.species or "").strip().lower()

        if species == "elf":
            lineage = self.species_traits.get("Elven Lineage", "")
            mapping = {
                "drow": {
                    "name": "Drow Magic",
                    "damage_type": "radiant",
                    "damage_die": 8,
                    "range": 3,
                    "target_required": True,
                },
                "high elf": {
                    "name": "High Elf Cantrip",
                    "damage_type": "force",
                    "damage_die": 8,
                    "range": 3,
                    "target_required": True,
                },
                "wood elf": {
                    "name": "Wood Elf Cantrip",
                    "damage_type": "poison",
                    "damage_die": 8,
                    "range": 3,
                    "target_required": True,
                },
            }
            self.species_magic = mapping.get(str(lineage).strip().lower())
            return

        if species == "gnome":
            lineage = self.species_traits.get("Gnomish Lineage", "")
            mapping = {
                "forest gnome": {
                    "name": "Forest Gnome Magic",
                    "damage_type": "psychic",
                    "damage_die": 8,
                    "range": 3,
                    "target_required": True,
                },
                "rock gnome": {
                    "name": "Rock Gnome Magic",
                    "damage_type": "thunder",
                    "damage_die": 8,
                    "range": 3,
                    "target_required": True,
                },
            }
            self.species_magic = mapping.get(str(lineage).strip().lower())
            return

        if species == "tiefling":
            legacy = self.species_traits.get("Fiendish Legacy", "")
            mapping = {
                "abyssal": {
                    "name": "Abyssal Magic",
                    "damage_type": "poison",
                    "damage_die": 10,
                    "range": 2,
                    "target_required": True,
                },
                "chthonic": {
                    "name": "Chthonic Magic",
                    "damage_type": "necrotic",
                    "damage_die": 10,
                    "range": 3,
                    "target_required": True,
                },
                "infernal": {
                    "name": "Infernal Magic",
                    "damage_type": "fire",
                    "damage_die": 10,
                    "range": 3,
                    "target_required": True,
                },
            }
            self.species_magic = mapping.get(str(legacy).strip().lower())
            return

        self.species_magic = None

    def has_species_magic(self) -> bool:
        return isinstance(self.species_magic, dict)

    def get_species_magic_label(self) -> str:
        if not self.has_species_magic():
            return "Species Magic"
        return self.species_magic.get("name", "Species Magic")

    def _get_cantrip_dice_count(self) -> int:
        if self.level >= 17:
            return 4
        if self.level >= 11:
            return 3
        if self.level >= 5:
            return 2
        return 1

    def get_species_magic_range(self) -> int:
        if not self.has_species_magic():
            return 0
        return int(self.species_magic.get("range", 0))

    def use_species_magic(self, target, log_fn=None) -> str:
        """Cast lineage/legacy species magic as a lightweight ranged spell attack."""
        if not self.has_species_magic():
            msg = f"{self.name} has no species magic available."
            if log_fn:
                log_fn(msg)
            return msg

        if target is None:
            msg = f"{self.name} needs a target for {self.get_species_magic_label()}."
            if log_fn:
                log_fn(msg)
            return msg

        roll = self.roll_d20()
        total = roll + self.attack_bonus - self.get_attack_roll_penalty()
        target_ac = target.get_ac() if hasattr(target, "get_ac") else target.ac
        target_ac += getattr(target, "temp_ac_bonus", 0)
        hit = (roll == 20) or (total >= target_ac)

        spell_name = self.get_species_magic_label()
        damage_type = self.species_magic.get("damage_type", "force")
        die_size = int(self.species_magic.get("damage_die", 8))

        if not hit:
            msg = f"{self.name} casts {spell_name}: {roll}+{self.attack_bonus}={total} vs AC {target_ac} -> MISS"
            if log_fn:
                log_fn(msg)
            return msg

        dice_count = self._get_cantrip_dice_count()
        raw_damage = dice.roll_dice(dice_count, die_size)
        if roll == 20:
            raw_damage += dice.roll_dice(dice_count, die_size)

        resisted = False
        dealt = raw_damage
        if hasattr(target, "take_damage"):
            dealt, resisted = target.take_damage(raw_damage, damage_type=damage_type, source=self, log_fn=log_fn)
        else:
            target.hp -= raw_damage

        notes = " (resisted)" if resisted else ""
        msg = (
            f"{self.name} casts {spell_name}: {roll}+{self.attack_bonus}={total} vs AC {target_ac} "
            f"-> HIT for {dealt} {damage_type} damage{notes} (target HP {max(target.hp, 0)})"
        )
        if log_fn:
            log_fn(msg)
        return msg

    def _parse_ancestry_damage_type(self, ancestry: str):
        if not isinstance(ancestry, str):
            return None
        lower = ancestry.lower()
        if "acid" in lower:
            return "acid"
        if "cold" in lower:
            return "cold"
        if "fire" in lower:
            return "fire"
        if "lightning" in lower:
            return "lightning"
        if "poison" in lower:
            return "poison"
        return None

    def get_proficiency_bonus(self) -> int:
        """Return proficiency bonus by level using 2024/SRD progression."""
        return 2 + max(0, (self.level - 1) // 4)

    def _refresh_breath_weapon_uses(self) -> None:
        if (self.species or "").strip().lower() != "dragonborn":
            self.breath_weapon_uses_max = 0
            self.breath_weapon_uses_remaining = 0
            return
        self.breath_weapon_uses_max = self.get_proficiency_bonus()
        if self.breath_weapon_uses_remaining <= 0:
            self.breath_weapon_uses_remaining = self.breath_weapon_uses_max

    def get_breath_weapon_damage_dice(self) -> int:
        """Return number of d10 for Dragonborn Breath Weapon scaling by level."""
        if self.level >= 17:
            return 4
        if self.level >= 11:
            return 3
        if self.level >= 5:
            return 2
        return 1

    def can_use_breath_weapon(self) -> bool:
        return self.breath_weapon_uses_remaining > 0 and bool(self.breath_weapon_damage_type)

    def use_breath_weapon(self, target, log_fn=None) -> str:
        """Use Dragonborn Breath Weapon on one target (first-pass single-target implementation)."""
        if not self.can_use_breath_weapon():
            msg = f"{self.name} cannot use Breath Weapon right now."
            if log_fn:
                log_fn(msg)
            return msg

        self.breath_weapon_uses_remaining -= 1
        dice_count = self.get_breath_weapon_damage_dice()
        raw_damage = dice.roll_dice(dice_count, 10)

        resisted = False
        dealt = raw_damage
        if hasattr(target, "take_damage"):
            dealt, resisted = target.take_damage(raw_damage, damage_type=self.breath_weapon_damage_type, source=self, log_fn=log_fn)
        else:
            target.hp -= raw_damage

        notes = " (resisted)" if resisted else ""
        msg = (
            f"{self.name} unleashes Breath Weapon ({self.breath_weapon_damage_type}) "
            f"for {dealt} damage{notes}. Uses left: {self.breath_weapon_uses_remaining}/{self.breath_weapon_uses_max}."
        )
        if log_fn:
            log_fn(msg)
        return msg

    def take_damage(self, amount: int, damage_type: str = "physical", source=None, log_fn=None) -> tuple[int, bool]:
        """Apply incoming damage with resistance handling. Returns (damage_taken, resisted)."""
        incoming = max(0, int(amount))
        dtype = (damage_type or "physical").strip().lower()
        resisted = False

        if self.temp_hp > 0 and incoming > 0:
            absorbed = min(self.temp_hp, incoming)
            self.temp_hp -= absorbed
            incoming -= absorbed

        if self.raging and dtype in {"physical", "bludgeoning", "piercing", "slashing"}:
            incoming = max(1, incoming // 2)
            resisted = True

        if (self.species or "").strip().lower() == "dwarf" and dtype == "poison":
            incoming = max(1, incoming // 2)
            resisted = True

        if dtype in self.damage_resistances:
            incoming = max(1, incoming // 2)
            resisted = True

        if (self.species or "").strip().lower() == "goliath" and self.giant_ancestry_uses_remaining > 0:
            if self.giant_ancestry == "stone" and incoming > 0:
                reduction = max(0, dice.roll_dice(1, 12) + self.get_ability_modifier("CON"))
                if reduction > 0:
                    incoming = max(0, incoming - reduction)
                    self.giant_ancestry_uses_remaining -= 1
                    if log_fn:
                        log_fn(f"{self.name} uses Stone's Endurance and reduces damage by {reduction}.")
            elif self.giant_ancestry == "storm" and source is not None and incoming > 0:
                th_dmg = dice.roll_dice(1, 8)
                self.giant_ancestry_uses_remaining -= 1
                if hasattr(source, "take_damage"):
                    source.take_damage(th_dmg, damage_type="thunder", source=self, log_fn=log_fn)
                else:
                    source.hp -= th_dmg
                if log_fn:
                    log_fn(f"{self.name} uses Storm's Thunder for {th_dmg} damage to {source.name}.")

        self.hp -= incoming

        if self.hp <= 0 and self.relentless_endurance_available:
            self.hp = 1
            self.relentless_endurance_available = False
            if log_fn:
                log_fn(f"{self.name} uses Relentless Endurance and drops to 1 HP instead.")
        return incoming, resisted

    def _apply_goliath_on_hit_bonus(self, target):
        if (self.species or "").strip().lower() != "goliath":
            return {}
        if self.giant_ancestry_uses_remaining <= 0:
            return {}

        if self.giant_ancestry == "fire":
            self.giant_ancestry_uses_remaining -= 1
            return {"extra_damage": dice.roll_dice(1, 10), "label": "Fire's Burn"}
        if self.giant_ancestry == "frost":
            self.giant_ancestry_uses_remaining -= 1
            if hasattr(target, "speed_bonus_ft"):
                target.speed_bonus_ft -= 10
            return {"extra_damage": dice.roll_dice(1, 6), "label": "Frost's Chill"}
        if self.giant_ancestry == "hill":
            self.giant_ancestry_uses_remaining -= 1
            return {"extra_damage": 0, "label": "Hill's Tumble"}
        return {}

    def can_use_stonecunning(self) -> bool:
        return self.stonecunning_uses_remaining > 0

    def use_stonecunning(self) -> bool:
        if not self.can_use_stonecunning():
            return False
        self.stonecunning_uses_remaining -= 1
        self.tremorsense_range = 60
        self.tremorsense_rounds_remaining = 10
        return True

    def can_use_adrenaline_rush(self) -> bool:
        return self.adrenaline_rush_uses_remaining > 0

    def use_adrenaline_rush(self) -> int:
        if not self.can_use_adrenaline_rush():
            return 0
        self.adrenaline_rush_uses_remaining -= 1
        gained = self.get_proficiency_bonus()
        self.temp_hp += gained
        return gained

    def can_use_cloud_jaunt(self) -> bool:
        return self.giant_ancestry == "cloud" and self.giant_ancestry_uses_remaining > 0

    def use_cloud_jaunt(self) -> bool:
        if not self.can_use_cloud_jaunt():
            return False
        self.giant_ancestry_uses_remaining -= 1
        return True

    def can_use_large_form(self) -> bool:
        return self.goliath_large_form_available and self.level >= 5 and not self.goliath_large_form_active

    def activate_large_form(self) -> bool:
        if not self.can_use_large_form():
            return False
        self.goliath_large_form_active = True
        self.goliath_large_form_rounds_remaining = 10
        self.goliath_large_form_available = False
        self.speed_bonus_ft += 10
        return True

    def get_species_bonus_actions(self):
        actions = []
        if self.can_use_stonecunning():
            actions.append(("Stonecunning", "stonecunning", self.stonecunning_uses_remaining, self.stonecunning_uses_max))
        if self.can_use_adrenaline_rush():
            actions.append(("Adrenaline", "adrenaline_rush", self.adrenaline_rush_uses_remaining, self.adrenaline_rush_uses_max))
        if self.can_use_cloud_jaunt():
            actions.append(("Cloud Jaunt", "cloud_jaunt", self.giant_ancestry_uses_remaining, self.giant_ancestry_uses_max))
        if self.can_use_large_form():
            actions.append(("Large Form", "large_form", 1, 1))
        return actions

    def start_combat(self, auto_features=True):
        """Initialize per-combat feature state. Returns list of messages."""
        messages = []
        self.sneak_attack_used = False
        self.raging = False
        self.rage_rounds_remaining = 0
        if auto_features:
            rage_feature = self.get_feature("Rage")
            if rage_feature and rage_feature.use():
                self.raging = True
                self.rage_rounds_remaining = 10
                messages.append(f"{self.name} enters a Rage!")
        return messages

    def start_turn(self):
        """Reset per-turn feature state."""
        self.sneak_attack_used = False

    def end_round(self):
        """Advance round-based feature durations. Returns list of messages."""
        messages = []
        if self.raging:
            self.rage_rounds_remaining -= 1
            if self.rage_rounds_remaining <= 0:
                self.raging = False
                messages.append(f"{self.name}'s Rage fades.")
        if self.goliath_large_form_active:
            self.goliath_large_form_rounds_remaining -= 1
            if self.goliath_large_form_rounds_remaining <= 0:
                self.goliath_large_form_active = False
                self.speed_bonus_ft = max(0, self.speed_bonus_ft - 10)
                messages.append(f"{self.name}'s Large Form ends.")
        if self.tremorsense_rounds_remaining > 0:
            self.tremorsense_rounds_remaining -= 1
            if self.tremorsense_rounds_remaining <= 0:
                self.tremorsense_range = 0
        expired = self.tick_status_effects()
        for effect_name in expired:
            messages.append(f"{self.name} is no longer {effect_name}.")
        return messages

    def roll_initiative(self):
        """Roll initiative (d20 + initiative bonus).

        Returns a tuple `(total, roll)` where `total` is the final initiative
        (roll + initiative_bonus) and `roll` is the raw d20 roll. Returning the
        raw roll helps tie-breaking logic remain deterministic in tests.
        """
        roll = self.roll_d20()
        total = roll + self.initiative_bonus
        return total, roll

    def heal(self, amount):
        """Heal the character up to max_hp."""
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def use_potion(self, amount=7):
        """Consume a potion to heal. Returns healed amount or 0 if none.
        
        Args:
            amount: HP to restore (default 7, average of 2d4+2 from SRD Potion of Healing)
            
        Returns:
            Amount of HP actually healed, or 0 if no potions available.
        """
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

    def get_sneak_attack_dice(self) -> int:
        """Return number of d6 dice for sneak attack based on rogue level.
        
        D&D 5e Rogue progression:
        - Levels 1-4: 1d6
        - Levels 5-8: 2d6
        - Levels 9-12: 3d6
        - Levels 13-16: 4d6
        - Levels 17-20: 5d6
        """
        if self.class_name != "Rogue":
            return 0
        return max(1, (self.level + 3) // 4)

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
        self._refresh_breath_weapon_uses()
        self.spell_slots_max = get_spell_slots_max(self.class_name or "", self.level)
        self.restore_spell_slots()
        species = (self.species or "").strip().lower()
        if species == "dwarf":
            self.max_hp += 1
            self.hp += 1
            self.stonecunning_uses_max = self.get_proficiency_bonus()
            self.stonecunning_uses_remaining = self.stonecunning_uses_max
        if species == "orc":
            self.adrenaline_rush_uses_max = self.get_proficiency_bonus()
            self.adrenaline_rush_uses_remaining = self.adrenaline_rush_uses_max
        if species == "goliath":
            self.giant_ancestry_uses_max = self.get_proficiency_bonus()
            self.giant_ancestry_uses_remaining = self.giant_ancestry_uses_max

    def defend(self, ac_bonus=2):
        """Apply a temporary AC bonus for the rest of the round."""
        self.temp_ac_bonus = ac_bonus

    def heal_ally(self, target, amount=7):
        """Heal an allied character by consuming a potion if available.
        
        Args:
            target: Character to heal
            amount: HP to restore (default 7, average of 2d4+2 from SRD Potion of Healing)

        Returns:
            Amount of HP actually healed (0 if no potion available).
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
        if self.get_feature("Lay On Hands"):
            self.lay_on_hands_pool = 5 * self.level
        if (self.species or "").strip().lower() == "dragonborn":
            self.breath_weapon_uses_remaining = self.get_proficiency_bonus()
            self.breath_weapon_uses_max = self.breath_weapon_uses_remaining
        if (self.species or "").strip().lower() == "human":
            self.inspiration_die = max(self.inspiration_die, 6)
        if (self.species or "").strip().lower() == "orc":
            self.relentless_endurance_available = True
            self.adrenaline_rush_uses_remaining = self.get_proficiency_bonus()
            self.adrenaline_rush_uses_max = self.adrenaline_rush_uses_remaining
        if (self.species or "").strip().lower() == "goliath":
            self.giant_ancestry_uses_remaining = self.get_proficiency_bonus()
            self.giant_ancestry_uses_max = self.giant_ancestry_uses_remaining
            self.goliath_large_form_available = True
            self.goliath_large_form_active = False
            self.goliath_large_form_rounds_remaining = 0
        if (self.species or "").strip().lower() == "dwarf":
            self.stonecunning_uses_remaining = self.get_proficiency_bonus()
            self.stonecunning_uses_max = self.stonecunning_uses_remaining
        self.restore_spell_slots()
    
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

    def activate_rage(self) -> bool:
        """Activate Rage if available. Returns True if activated."""
        if self.raging:
            return False
        rage_feature = self.get_feature("Rage")
        if rage_feature and rage_feature.use():
            self.raging = True
            self.rage_rounds_remaining = 10
            return True
        return False

    def use_second_wind(self) -> int:
        """Use Second Wind to heal. Returns healed amount (0 if unavailable)."""
        feature = self.get_feature("Second Wind")
        if not feature or not feature.use():
            return 0
        heal_amount = dice.roll_dice(1, 10) + self.level
        return self.heal(heal_amount)

    def use_channel_divinity(self) -> int:
        """Use Channel Divinity to heal self. Returns healed amount."""
        feature = self.get_feature("Channel Divinity")
        if not feature or not feature.use():
            return 0
        wis_mod = self.get_ability_modifier("WIS")
        heal_amount = dice.roll_dice(2, 6) + max(1, wis_mod)
        return self.heal(heal_amount)

    def use_lay_on_hands(self, amount: int) -> int:
        """Spend Lay On Hands pool to heal. Returns healed amount."""
        if not self.get_feature("Lay On Hands"):
            return 0
        if amount <= 0:
            return 0
        spend = min(amount, self.lay_on_hands_pool)
        if spend <= 0:
            return 0
        self.lay_on_hands_pool -= spend
        return self.heal(spend)

    def use_bardic_inspiration(self) -> bool:
        """Grant self a d6 inspiration die for the next attack roll."""
        feature = self.get_feature("Bardic Inspiration")
        if not feature or not feature.use():
            return False
        self.inspiration_die = 6
        return True