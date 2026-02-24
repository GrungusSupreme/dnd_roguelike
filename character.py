"""Character model and combat actions."""
import dice
from class_features import get_class_features
from spell_data import (
    get_spell_slots_max,
    get_spell_definition,
    get_spellcasting_requirements,
    is_spellcaster_class,
    CLASS_CANTRIP_OPTIONS,
    CLASS_LEVEL1_SPELL_OPTIONS,
)
from character_creation_data import (
    class_has_weapon_mastery,
    class_is_weapon_proficient,
    get_class_weapon_mastery_count,
)


FEATURE_UNLOCK_LEVELS: dict[str, dict[str, int]] = {
    "Fighter": {
        "Action Surge": 2,
    },
    "Rogue": {
        "Cunning Action": 2,
        "Uncanny Dodge": 5,
    },
    "Druid": {
        "Wild Shape": 2,
    },
    "Bard": {
        "Expertise": 2,
    },
    "Monk": {
        "Monk's Focus": 2,
    },
    "Paladin": {
        "Smite": 2,
    },
    "Ranger": {
    },
    "Sorcerer": {
        "Font of Magic": 2,
    },
    "Warlock": {
        "Eldritch Invocations": 2,
    },
    "Wizard": {
        "Arcane Recovery": 2,
    },
}


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
        weapon_masteries=None,
        gold=0,
        spell_slots_current=None,
        spell_slots_max=None,
        fighting_style=None,
        expertise_skills=None,
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
        self.rage_extended_this_turn = False
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
        self.weapon_masteries = list(dict.fromkeys(list(weapon_masteries or [])))
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
        self.passive_perception = 10
        self.darkvision_range = 0
        self.hunters_mark_target_id = None
        self.smite_armed = False
        self.focus_empowered_rounds = 0
        self.wild_shape_rounds_remaining = 0
        self.wild_shape_speed_bonus_active = False
        self.breath_weapon_damage_type = None
        self.breath_weapon_uses_max = 0
        self.breath_weapon_uses_remaining = 0
        self.species_magic = None
        self.status_effects = {}
        self.vex_marks = {}
        # Fighting Style (Fighter lv1, Paladin lv2, Ranger lv2)
        self.fighting_style = fighting_style  # "Archery", "Defense", "Great Weapon Fighting", "Two-Weapon Fighting", or None
        # Expertise — doubled proficiency on chosen skills (Rogue lv1, Bard lv2)
        self.expertise_skills = list(expertise_skills or [])
        # Innate Sorcery state (Sorcerer lv1)
        self.innate_sorcery_active = False
        self.innate_sorcery_rounds_remaining = 0
        # Favored Enemy free casts (Ranger lv1): Hunter's Mark without slots
        self.favored_enemy_free_casts = 0
        self.favored_enemy_free_casts_max = 0
        if (self.class_name or "").strip() == "Ranger":
            self.favored_enemy_free_casts_max = 2
            self.favored_enemy_free_casts = 2
        # Origin feat state
        self.savage_attacker_used = False
        self.mi_free_cast_available = False
        self.mi_free_cast_spell = None
        self._initialize_species_features()
        self._initialize_origin_feats()
        
        # Equipment slots
        self.equipped_weapon = None  # Weapon object
        self.equipped_armor = None  # Armor object
        self.equipped_offhand = None  # Shield or secondary weapon
        self.inventory = []  # Carried items

    def get_speed_ft(self) -> int:
        """Return current speed in feet, including bonuses."""
        slow_penalty = 0
        if self.has_status_effect("slowed"):
            slow_penalty = int(self.status_effects.get("slowed", {}).get("potency", 10))
        return max(0, self.speed_ft + self.speed_bonus_ft - slow_penalty)

    def _initialize_spellcasting(self, spell_slots_current=None, spell_slots_max=None):
        class_name = self.class_name or ""
        if is_spellcaster_class(class_name):
            req = get_spellcasting_requirements(class_name)
            self.spellcasting_ability = str(req.get("ability", "INT"))
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
        return self.get_ability_modifier(str(self.spellcasting_ability))

    def get_spell_save_dc(self) -> int:
        """Return spell save DC = 8 + proficiency + spellcasting mod (+ Innate Sorcery)."""
        dc = 8 + self.get_proficiency_bonus() + self.get_spellcasting_modifier()
        # Innate Sorcery: +1 to Sorcerer spell save DC while active
        if self.innate_sorcery_active and (self.class_name or "").strip() == "Sorcerer":
            dc += 1
        return dc

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
        # Magic Initiate free cast (once per long rest, no slot needed)
        if self.mi_free_cast_available and spell_name == self.mi_free_cast_spell:
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
        # Magic Initiate free cast: consume it before using a regular slot
        if self.mi_free_cast_available and spell_name == self.mi_free_cast_spell:
            self.mi_free_cast_available = False
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
        # Prone penalty removed — now handled as real Disadvantage in attack()
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

    def roll_saving_throw(self, ability: str, dc: int, effect_tag: str = "", log_fn=None) -> tuple[bool, int]:
        mod = self.get_ability_modifier(ability)
        roll1 = self.roll_d20()
        adv_note = ""
        if self.has_save_advantage(ability, effect_tag):
            roll2 = self.roll_d20()
            adv_note = f" (Advantage d20s: {roll1}, {roll2})"
            roll = max(roll1, roll2)
        else:
            roll = roll1
        total = roll + mod
        passed = total >= dc
        result_word = "SAVE" if passed else "FAIL"
        if log_fn:
            log_fn(f"{self.name} {ability} save: d20({roll})+{mod} = {total} vs DC {dc} -> {result_word}{adv_note}")
        return passed, total

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
            spell_mod = max(0, self.get_spellcasting_modifier())
            # Healthy feat: reroll 1s on healing dice
            if self.has_origin_feat("Healthy"):
                base_heal_roll = self._roll_dice_reroll_ones(heal_dice[0], heal_dice[1])
                heal_amount = base_heal_roll + spell_mod
            else:
                base_heal_roll = dice.roll_dice(heal_dice[0], heal_dice[1])
                heal_amount = base_heal_roll + spell_mod
            heal_target = target if target is not None else self
            healed = heal_target.heal(heal_amount)
            heal_detail = f"{heal_dice[0]}d{heal_dice[1]}({base_heal_roll})+{spell_mod}"
            msg = f"{self.name} casts {spell_name} [{heal_detail} = {heal_amount}] and restores {healed} HP to {heal_target.name}."
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

        # Innate Sorcery: Advantage on Sorcerer spell attack rolls while active
        spell_adv = False
        if self.innate_sorcery_active and (self.class_name or "").strip() == "Sorcerer":
            spell_adv = True

        if spell.get("hit_type") == "auto":
            hit = True
            total = roll + spell_attack_bonus
        else:
            if spell_adv:
                roll2 = self.roll_d20()
                total = max(roll, roll2) + spell_attack_bonus
                hit = (max(roll, roll2) == 20) or (total >= target_ac)
            else:
                total = roll + spell_attack_bonus
                hit = (roll == 20) or (total >= target_ac)

        if not hit:
            adv_note = f" (Innate Sorcery Adv d20s: {roll}, {roll2})" if spell_adv else ""
            msg = f"{self.name} casts {spell_name}: d20({roll})+{spell_attack_bonus}={total} vs AC {target_ac} -> MISS{adv_note}"
            if log_fn:
                log_fn(msg)
            return msg

        base_spell_dice = dice.roll_dice(damage_tuple[0], damage_tuple[1])
        raw_damage = base_spell_dice
        dmg_detail = f"{damage_tuple[0]}d{damage_tuple[1]}({base_spell_dice})"
        if spell_name.strip().lower() == "eldritch blast" and self.get_feature("Eldritch Invocations"):
            cha_bonus = max(0, self.get_ability_modifier("CHA"))
            raw_damage += cha_bonus
            dmg_detail += f"+CHA({cha_bonus})"
        flat_bonus = int(spell.get("flat_bonus", 0))
        if flat_bonus:
            raw_damage += flat_bonus
            dmg_detail += f"+{flat_bonus}"
        crit_detail = ""
        if roll == 20 and spell.get("hit_type") != "auto":
            crit_dice = dice.roll_dice(damage_tuple[0], damage_tuple[1])
            raw_damage += crit_dice
            crit_detail = f" +crit {damage_tuple[0]}d{damage_tuple[1]}({crit_dice})"

        resisted = False
        dealt = raw_damage
        if hasattr(enemy, "take_damage"):
            dealt, resisted = enemy.take_damage(raw_damage, damage_type=damage_type, source=self, log_fn=log_fn)
        else:
            enemy.hp -= raw_damage

        notes = " (resisted)" if resisted else ""
        if spell_adv:
            notes += f" (Innate Sorcery Adv d20s: {roll}, {roll2})"
        msg = (
            f"{self.name} casts {spell_name}: d20({roll})+{spell_attack_bonus}={total} vs AC {target_ac} "
            f"-> HIT for {dealt} {damage_type} damage [{dmg_detail}{crit_detail}]{notes} (target HP {max(enemy.hp, 0)})"
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
        base_aoe_dice = dice.roll_dice(damage_tuple[0], damage_tuple[1])
        raw_damage = base_aoe_dice
        dmg_detail = f"{damage_tuple[0]}d{damage_tuple[1]}({base_aoe_dice})"

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
        msg = f"{self.name} casts {spell_name} for {raw_damage} {damage_type} damage [{dmg_detail}] in an area: {summary}."
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
                
                # Defense fighting style: +1 AC while wearing armor
                if self.fighting_style == "Defense":
                    ac += 1
                
                return ac + self.temp_ac_bonus
        
        # No armor: base 10 + DEX, with class-specific Unarmored Defense
        dex_mod = self.get_dex_modifier()
        class_key = (self.class_name or "").strip().lower()
        if class_key == "barbarian":
            return 10 + dex_mod + self.get_ability_modifier("CON") + self.temp_ac_bonus
        if class_key == "monk":
            return 10 + dex_mod + self.get_ability_modifier("WIS") + self.temp_ac_bonus
        return 10 + dex_mod + self.temp_ac_bonus

    def get_martial_arts_die(self) -> int:
        """Return the Martial Arts die size for a Monk, or 0 if not applicable.

        SRD 5.2.1 Monk table:
        Level 1-4  -> d6
        Level 5-10 -> d8
        Level 11-16 -> d10
        Level 17+  -> d12
        """
        if (self.class_name or "").strip() != "Monk":
            return 0
        if not self.get_feature("Martial Arts"):
            return 0
        level = int(getattr(self, "level", 1))
        if level >= 17:
            return 12
        if level >= 11:
            return 10
        if level >= 5:
            return 8
        return 6

    def is_monk_weapon(self, weapon=None) -> bool:
        """Return True if *weapon* (or equipped weapon) qualifies as a Monk weapon.

        SRD 5.2.1: Simple Melee weapons and Martial Melee weapons with the
        Light property count as Monk weapons.
        """
        if (self.class_name or "").strip() != "Monk":
            return False
        from items import Weapon
        w = weapon or self.equipped_weapon
        if not w or not isinstance(w, Weapon):
            return False
        prof = str(getattr(w, "proficiency_type", ""))
        if prof == "Simple Melee":
            return True
        if "Martial" in prof and "Melee" in prof and w.has_property("Light"):
            return True
        return False

    def _monk_unarmored(self) -> bool:
        """Return True if this Monk meets the Martial Arts armour condition."""
        return self.equipped_armor is None

    def _is_gwf_eligible(self) -> bool:
        """Return True if Great Weapon Fighting applies to the current weapon.

        SRD: The weapon must have the Two-Handed or Versatile property and
        be held with two hands (i.e. no offhand equipped for Versatile).
        """
        if self.fighting_style != "Great Weapon Fighting":
            return False
        if not self.equipped_weapon:
            return False
        from items import Weapon
        if not isinstance(self.equipped_weapon, Weapon):
            return False
        if self.equipped_weapon.has_property("Two-Handed"):
            return True
        if self.equipped_weapon.has_property("Versatile") and self.equipped_offhand is None:
            return True
        return False

    def _roll_gwf_dice(self, num: int, die: int) -> int:
        """Roll damage dice with Great Weapon Fighting: treat 1s and 2s as 3."""
        total = 0
        for _ in range(num):
            result = dice.roll_dice(1, die)
            if result <= 2:
                result = 3
            total += result
        return total

    def get_damage_dice(self) -> tuple[int, int]:
        """Return (dmg_num, dmg_die) from equipped weapon.

        For Monks wielding a Monk weapon, the Martial Arts die replaces the
        weapon die when it is higher (SRD: "in place of the normal damage").
        """
        if self.equipped_weapon:
            from items import Weapon
            if isinstance(self.equipped_weapon, Weapon):
                if (
                    self.equipped_weapon.versatile_dmg_die
                    and self.equipped_offhand is None
                    and self.get_attack_range() <= 1
                ):
                    base_die = int(self.equipped_weapon.versatile_dmg_die)
                else:
                    base_die = self.equipped_weapon.dmg_die
                dmg_num = self.equipped_weapon.dmg_num

                # Martial Arts die upgrade for Monk weapons
                ma_die = self.get_martial_arts_die()
                if ma_die and self.is_monk_weapon() and self._monk_unarmored():
                    base_die = max(base_die, ma_die)

                return (dmg_num, base_die)

        # Fallback to character baseline values (used by monsters and unarmed templates)
        return (self.dmg_num, self.dmg_die)

    def _get_weapon_attack_ability_modifier(self) -> int:
        """Return the ability modifier used for weapon attack and damage rolls.

        Rules:
        - Ranged weapons use DEX
        - Finesse melee weapons can use STR or DEX (choose higher)
        - Monk Dexterous Attacks: Monk weapons / unarmed use DEX if higher (SRD 5.2.1)
        - Other melee weapons use STR
        """
        str_mod = self.get_ability_modifier("STR")
        dex_mod = self.get_ability_modifier("DEX")

        if not self.equipped_weapon:
            # Unarmed — Monks use Dexterous Attacks (DEX if higher)
            if self.get_martial_arts_die() and self._monk_unarmored():
                return max(str_mod, dex_mod)
            return str_mod

        from items import Weapon
        if not isinstance(self.equipped_weapon, Weapon):
            return str_mod

        weapon = self.equipped_weapon
        proficiency_type = str(getattr(weapon, "proficiency_type", ""))
        if "Ranged" in proficiency_type:
            return dex_mod

        if bool(getattr(weapon, "finesse", False)):
            return max(str_mod, dex_mod)

        # Monk Dexterous Attacks — use DEX on Monk weapons if higher
        if self.is_monk_weapon(weapon) and self._monk_unarmored():
            return max(str_mod, dex_mod)

        return str_mod

    def get_attack_bonus_total(self) -> int:
        """Return effective attack bonus for current weapon state."""
        if self.equipped_weapon:
            bonus = self._get_weapon_attack_ability_modifier() + self.get_proficiency_bonus()
            # Archery fighting style: +2 to ranged weapon attack rolls
            if self.fighting_style == "Archery":
                from items import Weapon
                if isinstance(self.equipped_weapon, Weapon):
                    prof_type = str(getattr(self.equipped_weapon, "proficiency_type", ""))
                    if "Ranged" in prof_type or getattr(self.equipped_weapon, "attack_range", 1) > 1:
                        bonus += 2
            return bonus
        return self.attack_bonus

    def get_weapon_mastery(self) -> str:
        if not self.equipped_weapon:
            return ""
        if not class_has_weapon_mastery(self.class_name or ""):
            return ""

        weapon_name = str(getattr(self.equipped_weapon, "name", "")).strip()
        if weapon_name not in self.weapon_masteries:
            return ""

        if not class_is_weapon_proficient(self.class_name or "", weapon_name, self.equipped_weapon):
            return ""

        return str(getattr(self.equipped_weapon, "mastery", ""))

    def can_use_weapon_mastery(self, weapon=None) -> bool:
        target_weapon = weapon or self.equipped_weapon
        if not target_weapon:
            return False
        if not class_has_weapon_mastery(self.class_name or ""):
            return False
        weapon_name = str(getattr(target_weapon, "name", "")).strip()
        if weapon_name not in self.weapon_masteries:
            return False
        if not class_is_weapon_proficient(self.class_name or "", weapon_name, target_weapon):
            return False
        return bool(str(getattr(target_weapon, "mastery", "")).strip())

    def get_weapon_mastery_limit(self) -> int:
        return get_class_weapon_mastery_count(self.class_name or "")

    def get_damage_bonus(self) -> int:
        """Return total damage bonus from weapon + ability."""
        if not self.equipped_weapon:
            return self.dmg_bonus

        bonus = self._get_weapon_attack_ability_modifier()

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

        # Fallback to character baseline range
        return self.attack_range

    def is_alive(self):
        return self.hp > 0

    def attack(self, target, log_fn=None, target_distance: int | None = None):
        roll1 = self.roll_d20()
        roll2: int | None = None
        weapon = self.equipped_weapon
        mastery = self.get_weapon_mastery().lower()

        advantage_reasons: list[str] = []
        disadvantage_reasons: list[str] = []

        # Attacking from stealth grants advantage (used by sneaky enemies)
        if getattr(self, '_stealth_advantage', False):
            advantage_reasons.append("Unseen Attacker")
            self._stealth_advantage = False

        # Vex weapon mastery grants advantage on next attack vs target
        if id(target) in self.vex_marks:
            advantage_reasons.append("Vex")

        # Sapped condition grants disadvantage
        if self.has_status_effect("sapped"):
            disadvantage_reasons.append("Sapped")

        # Prone attacker has Disadvantage on attack rolls (SRD 5.2.1)
        if self.has_status_effect("prone"):
            disadvantage_reasons.append("Prone")

        # Prone target: melee (<=5ft) = Advantage, ranged = Disadvantage (SRD 5.2.1)
        if hasattr(target, "has_status_effect") and target.has_status_effect("prone"):
            if target_distance is not None and target_distance <= 1:
                advantage_reasons.append("Target prone (melee)")
            elif target_distance is not None and target_distance > 1:
                disadvantage_reasons.append("Target prone (ranged)")

        from items import Weapon
        is_ranged_attack = False
        if isinstance(weapon, Weapon):
            proficiency_type = str(getattr(weapon, "proficiency_type", ""))
            is_ranged_attack = "Ranged" in proficiency_type or getattr(weapon, "attack_range", 1) > 1
        else:
            is_ranged_attack = self.get_attack_range() > 1

        if is_ranged_attack and target_distance is not None and target_distance <= 1:
            disadvantage_reasons.append("Ranged in melee")

        if isinstance(weapon, Weapon) and weapon.has_property("Heavy"):
            if "Ranged" in proficiency_type or getattr(weapon, "attack_range", 1) > 1:
                if self.ability_scores.get("DEX", 10) < 13:
                    disadvantage_reasons.append("Heavy ranged STR/DEX gate")
            elif self.ability_scores.get("STR", 10) < 13:
                disadvantage_reasons.append("Heavy STR gate")

        has_advantage = len(advantage_reasons) > 0
        has_disadvantage = len(disadvantage_reasons) > 0

        attack_context_notes: list[str] = []
        if has_advantage and not has_disadvantage:
            roll2 = self.roll_d20()
            adv_label = ", ".join(dict.fromkeys(advantage_reasons))
            attack_context_notes.append(f"Advantage: {adv_label} d20s: {roll1}, {roll2}")
            roll = max(roll1, roll2)
        elif has_disadvantage and not has_advantage:
            roll2 = self.roll_d20()
            distinct = list(dict.fromkeys(disadvantage_reasons))
            attack_context_notes.append(f"Disadvantage: {', '.join(distinct)} d20s: {roll1}, {roll2}")
            roll = min(roll1, roll2)
        else:
            roll = roll1
            # If both advantage and disadvantage apply, they cancel out (SRD)
            if has_advantage and has_disadvantage:
                reasons = list(dict.fromkeys(advantage_reasons + disadvantage_reasons))
                attack_context_notes.append(f"Adv/Disadv cancel: {', '.join(reasons)}")

        if self.has_status_effect("sapped"):
            self.status_effects.pop("sapped", None)

        inspiration_bonus = 0
        if self.inspiration_die > 0:
            inspiration_bonus = dice.roll_dice(1, self.inspiration_die)
            self.inspiration_die = 0
        attack_penalty = self.get_attack_roll_penalty()
        effective_attack_bonus = self.get_attack_bonus_total() - attack_penalty
        total = roll + effective_attack_bonus + inspiration_bonus
        # Making an attack roll vs an enemy extends Rage (SRD 5.2.1)
        if self.raging:
            self.rage_extended_this_turn = True
        # Use dynamic AC calculation for target
        target_ac = target.get_ac() if hasattr(target, 'get_ac') else target.ac
        target_ac += getattr(target, "temp_ac_bonus", 0)
        hit = (roll == 20) or (total >= target_ac)
        if hit:
            # Use dynamic damage dice and bonus from equipped weapon
            dmg_num, dmg_die = self.get_damage_dice()
            dmg_bonus = self.get_damage_bonus()
            # Great Weapon Fighting: treat 1s and 2s as 3 on damage dice
            if self._is_gwf_eligible():
                base_dice_roll = self._roll_gwf_dice(dmg_num, dmg_die)
            else:
                base_dice_roll = dice.roll_dice(dmg_num, dmg_die)
            dmg = base_dice_roll + dmg_bonus
            dmg_detail = f"{dmg_num}d{dmg_die}({base_dice_roll})+{dmg_bonus}"
            # Savage Attacker: roll weapon damage twice, take higher (once per turn)
            if self.has_origin_feat("Savage Attacker") and not self.savage_attacker_used:
                if self._is_gwf_eligible():
                    second_dice = self._roll_gwf_dice(dmg_num, dmg_die)
                else:
                    second_dice = dice.roll_dice(dmg_num, dmg_die)
                second_total = second_dice + dmg_bonus
                if second_total > dmg:
                    dmg_detail = f"{dmg_num}d{dmg_die}({second_dice})+{dmg_bonus} [Savage: {base_dice_roll} vs {second_dice}]"
                    dmg = second_total
                else:
                    dmg_detail = f"{dmg_num}d{dmg_die}({base_dice_roll})+{dmg_bonus} [Savage: {base_dice_roll} vs {second_dice}]"
                self.savage_attacker_used = True
            crit_detail = ""
            if roll == 20:
                if self._is_gwf_eligible():
                    crit_dice = self._roll_gwf_dice(dmg_num, dmg_die)
                else:
                    crit_dice = dice.roll_dice(dmg_num, dmg_die)
                dmg += crit_dice
                crit_detail = f" +crit {dmg_num}d{dmg_die}({crit_dice})"
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
            resisted = False
            if hasattr(target, "take_damage"):
                dmg, resisted = target.take_damage(dmg, damage_type="physical", source=self, log_fn=log_fn)
            else:
                target.hp -= dmg
            total_dealt = int(dmg)

            if id(target) == self.hunters_mark_target_id and target.is_alive():
                mark_damage = dice.roll_dice(1, 4)
                if hasattr(target, "take_damage"):
                    mark_dealt, _ = target.take_damage(mark_damage, damage_type="physical", source=self, log_fn=log_fn)
                else:
                    target.hp -= mark_damage
                    mark_dealt = mark_damage
                total_dealt += int(mark_dealt)
                extra_notes.append(f"Hunter's Mark +{mark_dealt}")

            if self.focus_empowered_rounds > 0 and target.is_alive():
                focus_damage = dice.roll_dice(1, 4)
                if hasattr(target, "take_damage"):
                    focus_dealt, _ = target.take_damage(focus_damage, damage_type="force", source=self, log_fn=log_fn)
                else:
                    target.hp -= focus_damage
                    focus_dealt = focus_damage
                total_dealt += int(focus_dealt)
                extra_notes.append(f"Monk Focus +{focus_dealt}")

            if self.smite_armed and target.is_alive():
                smite_damage = dice.roll_dice(2, 6)
                if hasattr(target, "take_damage"):
                    smite_dealt, _ = target.take_damage(smite_damage, damage_type="radiant", source=self, log_fn=log_fn)
                else:
                    target.hp -= smite_damage
                    smite_dealt = smite_damage
                total_dealt += int(smite_dealt)
                self.smite_armed = False
                extra_notes.append(f"Smite +{smite_dealt}")

            target_hp = max(target.hp, 0)
            notes = ""
            all_notes = list(attack_context_notes)
            all_notes.extend(extra_notes)
            if all_notes:
                notes = " (" + ", ".join(all_notes) + ")"
            if resisted:
                notes = f"{notes} (resisted)" if notes else " (resisted)"

            if mastery == "vex":
                self.vex_marks[id(target)] = 2
                notes = f"{notes} (Vex prepared)" if notes else " (Vex prepared)"
            elif mastery == "sap" and hasattr(target, "apply_status_effect"):
                target.apply_status_effect("sapped", rounds=1)
                notes = f"{notes} (Sap)" if notes else " (Sap)"
            elif mastery == "slow" and hasattr(target, "apply_status_effect"):
                target.apply_status_effect("slowed", rounds=1, potency=10)
                notes = f"{notes} (Slow -10 ft)" if notes else " (Slow -10 ft)"
            elif mastery == "topple" and hasattr(target, "roll_saving_throw"):
                dc = 8 + self._get_weapon_attack_ability_modifier() + self.get_proficiency_bonus()
                saved, _ = target.roll_saving_throw("CON", dc, log_fn=log_fn)
                if not saved and hasattr(target, "apply_status_effect"):
                    target.apply_status_effect("prone", rounds=1)
                    notes = f"{notes} (Topple -> Prone)" if notes else " (Topple -> Prone)"

            msg = f"{self.name} rolls d20({roll})+{effective_attack_bonus} = {total} vs AC {target_ac} -> HIT for {total_dealt} dmg [{dmg_detail}{crit_detail}]{notes} (target HP {target_hp})"
        else:
            if mastery == "graze":
                graze_dmg = max(0, self._get_weapon_attack_ability_modifier())
                if graze_dmg > 0:
                    resisted = False
                    if hasattr(target, "take_damage"):
                        graze_dmg, resisted = target.take_damage(graze_dmg, damage_type="physical", source=self, log_fn=log_fn)
                    else:
                        target.hp -= graze_dmg
                    resist_note = " (resisted)" if resisted else ""
                    context_note = f" ({', '.join(attack_context_notes)})" if attack_context_notes else ""
                    msg = f"{self.name} rolls d20({roll})+{effective_attack_bonus} = {total} vs AC {target_ac} -> MISS{context_note}, Graze deals {graze_dmg}{resist_note}"
                    if log_fn:
                        log_fn(msg)
                    else:
                        print(msg)
                    return msg
            target_ac = target.get_ac() if hasattr(target, 'get_ac') else target.ac
            context_note = f" ({', '.join(attack_context_notes)})" if attack_context_notes else ""
            msg = f"{self.name} rolls d20({roll})+{effective_attack_bonus} = {total} vs AC {target_ac} -> MISS{context_note}"
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

    # ------------------------------------------------------------------
    # Origin Feats
    # ------------------------------------------------------------------

    def has_origin_feat(self, name: str) -> bool:
        """Return True if the character has the given origin feat."""
        return name in self.origin_feats

    def _get_mi_class(self, feat_name: str) -> str | None:
        """Extract the class from a Magic Initiate feat name, e.g. 'Magic Initiate (Wizard)' -> 'Wizard'."""
        if feat_name.startswith("Magic Initiate (") and feat_name.endswith(")"):
            return feat_name[len("Magic Initiate ("):-1]
        return None

    def _initialize_origin_feats(self) -> None:
        """Apply origin feat effects at character creation / load time."""
        for feat in self.origin_feats:
            # --- Magic Initiate ---
            mi_class = self._get_mi_class(feat)
            if mi_class:
                # Auto-assign 2 cantrips + 1 level-1 spell from the MI class list
                cantrips = CLASS_CANTRIP_OPTIONS.get(mi_class, [])
                spells_l1 = CLASS_LEVEL1_SPELL_OPTIONS.get(mi_class, [])
                added = 0
                for c in cantrips:
                    if c not in self.spells:
                        self.spells.append(c)
                        added += 1
                    if added >= 2:
                        break
                if spells_l1:
                    chosen = spells_l1[0]
                    if chosen not in self.spells:
                        self.spells.append(chosen)
                    self.mi_free_cast_spell = chosen
                    self.mi_free_cast_available = True
                # Ensure at minimum 1 level-1 slot for the MI spell
                if self.spell_slots_max.get(1, 0) < 1:
                    self.spell_slots_max[1] = 1
                    self.spell_slots_current[1] = 1
                # Set spellcasting ability based on MI class
                MI_ABILITY = {"Cleric": "WIS", "Druid": "WIS", "Wizard": "INT"}
                if not is_spellcaster_class(self.class_name or ""):
                    self.spellcasting_ability = MI_ABILITY.get(mi_class, "INT")
                continue

            # --- Meaty: +2 HP per level ---
            if feat == "Meaty":
                bonus = 2 * max(1, self.level)
                self.max_hp += bonus
                self.hp += bonus
                continue

    def _roll_dice_reroll_ones(self, num: int, die: int) -> int:
        """Roll dice, rerolling any 1s once (for Healthy / Iron Fist feats)."""
        total = 0
        for _ in range(num):
            result = dice.roll_dice(1, die)
            if result == 1:
                result = dice.roll_dice(1, die)
            total += result
        return total

    def get_buy_cost(self, base_cost: int) -> int:
        """Return the gold cost after applying Crafty discount (20% off).

        Call this whenever the player buys something (not upgrades).
        """
        if self.has_origin_feat("Crafty"):
            return max(1, int(base_cost * 0.8))
        return base_cost

    def has_species_magic(self) -> bool:
        return isinstance(self.species_magic, dict)

    def get_species_magic_label(self) -> str:
        if not self.has_species_magic():
            return "Species Magic"
        species_magic = self.species_magic if isinstance(self.species_magic, dict) else {}
        return str(species_magic.get("name", "Species Magic"))

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
        species_magic = self.species_magic if isinstance(self.species_magic, dict) else {}
        return int(species_magic.get("range", 0))

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
        species_magic = self.species_magic if isinstance(self.species_magic, dict) else {}
        damage_type = str(species_magic.get("damage_type", "force"))
        die_size = int(species_magic.get("damage_die", 8))

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

    def get_skill_bonus(self, skill_name: str, ability: str | None = None) -> int:
        """Return total bonus for a skill check (ability mod + proficiency + expertise).

        Args:
            skill_name: The skill name (e.g. 'Stealth', 'Perception').
            ability: Override ability for the check. If None, uses the standard mapping.
        """
        SKILL_ABILITIES: dict[str, str] = {
            "Acrobatics": "DEX", "Animal Handling": "WIS", "Arcana": "INT",
            "Athletics": "STR", "Deception": "CHA", "History": "INT",
            "Insight": "WIS", "Intimidation": "CHA", "Investigation": "INT",
            "Medicine": "WIS", "Nature": "INT", "Perception": "WIS",
            "Performance": "CHA", "Persuasion": "CHA", "Religion": "INT",
            "Sleight of Hand": "DEX", "Stealth": "DEX", "Survival": "WIS",
        }
        ability_key = ability or SKILL_ABILITIES.get(skill_name, "DEX")
        bonus = self.get_ability_modifier(ability_key)
        if skill_name in self.skill_proficiencies:
            prof = self.get_proficiency_bonus()
            if skill_name in self.expertise_skills:
                prof *= 2  # Expertise doubles proficiency
            bonus += prof
        return bonus

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
        """Apply incoming damage with resistance handling. Returns (damage_taken, resisted).

        Order of operations (per D&D 5e SRD):
        1. Apply resistance / vulnerability to determine final damage.
        2. Apply special reductions (e.g. Stone's Endurance).
        3. Temp HP absorbs remaining damage.
        4. Leftover damage is subtracted from real HP.
        """
        incoming = max(0, int(amount))
        dtype = (damage_type or "physical").strip().lower()
        resisted = False

        # --- 1. Resistance / vulnerability ---
        if self.raging and dtype in {"physical", "bludgeoning", "piercing", "slashing"}:
            incoming = max(1, incoming // 2)
            resisted = True

        if (self.species or "").strip().lower() == "dwarf" and dtype == "poison":
            incoming = max(1, incoming // 2)
            resisted = True

        if dtype in self.damage_resistances:
            incoming = max(1, incoming // 2)
            resisted = True

        # --- 2. Special reductions ---
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

        # --- 3. Temp HP absorbs remaining damage ---
        if self.temp_hp > 0 and incoming > 0:
            absorbed = min(self.temp_hp, incoming)
            self.temp_hp -= absorbed
            incoming -= absorbed

        # --- 4. Apply to real HP ---
        self.hp -= incoming

        if self.hp <= 0 and self.relentless_endurance_available:
            self.hp = 1
            self.relentless_endurance_available = False
            if log_fn:
                log_fn(f"{self.name} uses Relentless Endurance and drops to 1 HP instead.")
        return incoming, resisted

    def get_on_hit_feature_options(self, target=None) -> list[dict]:
        """Return optional features the player may activate after hitting with an attack.

        Each option has: id, label, description.
        """
        options: list[dict] = []
        for feature_id, definition in self._get_on_hit_feature_registry().items():
            if not self._can_use_on_hit_feature(definition):
                continue
            uses_text = f"({self.giant_ancestry_uses_remaining}/{self.giant_ancestry_uses_max})"
            options.append(
                {
                    "id": feature_id,
                    "label": f"{definition['name']} {uses_text}",
                    "description": definition["description"],
                }
            )
        return options

    def activate_on_hit_feature(self, feature_id: str, target=None, log_fn=None) -> str:
        """Activate an optional on-hit feature by id."""
        feature_key = (feature_id or "").strip().lower()
        registry = self._get_on_hit_feature_registry()
        if feature_key not in registry:
            return "No on-hit feature available."
        definition = registry[feature_key]

        if not self._can_use_on_hit_feature(definition):
            return "No uses remaining for this feature."
        if target is None:
            return "No target available for on-hit feature."

        self.giant_ancestry_uses_remaining -= 1
        return self._resolve_on_hit_feature(definition, target, log_fn)

    def _can_use_on_hit_feature(self, definition: dict) -> bool:
        if (self.species or "").strip().lower() != definition.get("species", ""):
            return False
        if definition.get("ancestry") and self.giant_ancestry != definition.get("ancestry"):
            return False
        if self.giant_ancestry_uses_remaining <= 0:
            return False
        return True

    def _get_on_hit_feature_registry(self) -> dict[str, dict]:
        return {
            "goliath_fire_burn": {
                "species": "goliath",
                "ancestry": "fire",
                "name": "Fire's Burn",
                "description": "On hit: deal an extra 1d10 fire damage.",
                "kind": "damage",
                "damage": (1, 10),
                "damage_type": "fire",
                "message": "Fire's Burn deals {dealt} fire damage{resist_note} to {target}.",
            },
            "goliath_frost_chill": {
                "species": "goliath",
                "ancestry": "frost",
                "name": "Frost's Chill",
                "description": "On hit: deal 1d6 cold damage and reduce speed by 10 ft until next turn.",
                "kind": "damage_and_status",
                "damage": (1, 6),
                "damage_type": "cold",
                "status": ("slowed", 1, 10),
                "message": "Frost's Chill deals {dealt} cold damage{resist_note} and slows {target}.",
            },
            "goliath_hill_tumble": {
                "species": "goliath",
                "ancestry": "hill",
                "name": "Hill's Tumble",
                "description": "On hit: knock the target prone.",
                "kind": "status",
                "status": ("prone", 1, 0),
                "message": "Hill's Tumble knocks {target} prone.",
            },
        }

    def _resolve_on_hit_feature(self, definition: dict, target, log_fn=None) -> str:
        kind = str(definition.get("kind", ""))
        target_name = getattr(target, "name", "target")

        dealt = 0
        resist_note = ""
        if kind in {"damage", "damage_and_status"}:
            dice_num, dice_die = definition.get("damage", (1, 6))
            rolled_damage = dice.roll_dice(int(dice_num), int(dice_die))
            damage_type = str(definition.get("damage_type", "physical"))
            resisted = False
            dealt = rolled_damage
            if hasattr(target, "take_damage"):
                dealt, resisted = target.take_damage(rolled_damage, damage_type=damage_type, source=self, log_fn=log_fn)
            else:
                target.hp -= rolled_damage
            resist_note = " (resisted)" if resisted else ""

        if kind in {"status", "damage_and_status"} and hasattr(target, "apply_status_effect"):
            status_name, rounds, potency = definition.get("status", ("", 0, 0))
            if status_name and rounds > 0:
                target.apply_status_effect(str(status_name), rounds=int(rounds), potency=int(potency))

        msg_template = str(definition.get("message", "Feature activated on {target}."))
        msg = msg_template.format(dealt=dealt, resist_note=resist_note, target=target_name)
        if log_fn:
            log_fn(msg)
        return msg

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
        self.temp_hp = max(self.temp_hp, gained)
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
        self.rage_extended_this_turn = False
        self.hunters_mark_target_id = None
        self.smite_armed = False
        self.focus_empowered_rounds = 0
        if auto_features:
            rage_feature = self.get_feature("Rage")
            if rage_feature and rage_feature.use():
                self.raging = True
                self.rage_rounds_remaining = 10
                self.rage_extended_this_turn = True
                messages.append(f"{self.name} enters a Rage!")
        return messages

    def start_turn(self):
        """Reset per-turn feature state."""
        self.sneak_attack_used = False
        self.savage_attacker_used = False
        if self.raging:
            self.rage_extended_this_turn = False
        expired_vex = []
        for target_id, rounds in self.vex_marks.items():
            next_rounds = int(rounds) - 1
            if next_rounds <= 0:
                expired_vex.append(target_id)
            else:
                self.vex_marks[target_id] = next_rounds
        for target_id in expired_vex:
            self.vex_marks.pop(target_id, None)

    def end_round(self):
        """Advance round-based feature durations. Returns list of messages."""
        messages = []
        if self.raging:
            if not self.rage_extended_this_turn:
                self.raging = False
                self.rage_rounds_remaining = 0
                messages.append(f"{self.name}'s Rage ends (not maintained).")
            else:
                self.rage_rounds_remaining -= 1
                if self.rage_rounds_remaining <= 0:
                    self.raging = False
                    messages.append(f"{self.name}'s Rage fades (max duration).")
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
        if self.focus_empowered_rounds > 0:
            self.focus_empowered_rounds -= 1
        if self.innate_sorcery_rounds_remaining > 0:
            self.innate_sorcery_rounds_remaining -= 1
            if self.innate_sorcery_rounds_remaining <= 0:
                self.innate_sorcery_active = False
                messages.append(f"{self.name}'s Innate Sorcery fades.")
        if self.wild_shape_rounds_remaining > 0:
            self.wild_shape_rounds_remaining -= 1
            if self.wild_shape_rounds_remaining <= 0 and self.wild_shape_speed_bonus_active:
                self.speed_bonus_ft = max(0, self.speed_bonus_ft - 10)
                self.wild_shape_speed_bonus_active = False
                messages.append(f"{self.name}'s Wild Shape fades.")
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
        # Alert feat: add Proficiency Bonus to initiative
        if self.has_origin_feat("Alert"):
            total += self.get_proficiency_bonus()
        return total, roll

    def heal(self, amount):
        """Heal the character up to max_hp."""
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def use_potion(self, amount=None):
        """Consume a potion to heal. Returns healed amount or 0 if none.
        
        Args:
            amount: HP to restore. If None, rolls 2d4+2 (SRD Potion of Healing).
                    Healthy feat rerolls 1s on the dice.
            
        Returns:
            Amount of HP actually healed, or 0 if no potions available.
        """
        if self.potions <= 0:
            return 0
        self.potions -= 1
        if amount is None:
            # Roll 2d4+2 for Potion of Healing
            if self.has_origin_feat("Healthy"):
                amount = self._roll_dice_reroll_ones(2, 4) + 2
            else:
                amount = dice.roll_dice(2, 4) + 2
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
        # Preserve Magic Initiate spell slot for non-casters
        if self.mi_free_cast_spell and self.spell_slots_max.get(1, 0) < 1:
            self.spell_slots_max[1] = 1
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
        # Meaty feat: +2 HP per level gained
        if self.has_origin_feat("Meaty"):
            self.max_hp += 2
            self.hp += 2

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
        feature = self.get_feature(feature_name)
        if not feature:
            return False
        return feature.use()

    def get_feature_unlock_level(self, feature_name: str) -> int:
        class_key = str(self.class_name or "").strip()
        by_class = FEATURE_UNLOCK_LEVELS.get(class_key, {})
        return int(by_class.get(feature_name, 1))

    def get_newly_unlocked_features(self, old_level: int, new_level: int) -> list[str]:
        start = max(1, int(old_level) + 1)
        end = max(start, int(new_level))
        gained: list[str] = []
        for feature in self.features:
            unlock_level = self.get_feature_unlock_level(feature.name)
            if start <= unlock_level <= end:
                gained.append(feature.name)
        return gained
    
    def get_feature(self, feature_name):
        """Get a feature by name.
        
        Args:
            feature_name: Name of the feature.
            
        Returns:
            ClassFeature object or None if not found.
        """
        for feature in self.features:
            if feature.name == feature_name:
                unlock_level = self.get_feature_unlock_level(feature_name)
                if self.level < unlock_level:
                    return None
                return feature
        return None
    
    def get_available_features(self):
        """Get list of features that have uses remaining.
        
        Returns:
            List of available ClassFeature objects.
        """
        available = []
        for feature in self.features:
            unlock_level = self.get_feature_unlock_level(feature.name)
            if self.level < unlock_level:
                continue
            if feature.uses_remaining > 0 or feature.max_uses is None:
                available.append(feature)
        return available
    
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
        self.smite_armed = False
        self.hunters_mark_target_id = None
        self.focus_empowered_rounds = 0
        self.innate_sorcery_active = False
        self.innate_sorcery_rounds_remaining = 0
        # Favored Enemy free casts reset on long rest
        if (self.class_name or "").strip() == "Ranger":
            self.favored_enemy_free_casts = self.favored_enemy_free_casts_max
        self.restore_spell_slots()
        # Restore Magic Initiate free cast on long rest
        if self.mi_free_cast_spell:
            self.mi_free_cast_available = True
    
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
            self.rage_extended_this_turn = True
            return True
        return False

    def extend_rage(self) -> bool:
        """Use a Bonus Action to extend Rage for another round (SRD 5.2.1).

        Returns True if rage was successfully extended.
        """
        if not self.raging:
            return False
        self.rage_extended_this_turn = True
        return True

    def activate_innate_sorcery(self) -> bool:
        """Activate Innate Sorcery as a Bonus Action (Sorcerer lv1). Returns True if activated.

        SRD 5.2.1: 2 uses per Long Rest. Lasts 1 minute (~10 rounds).
        While active: +1 spell save DC, Advantage on Sorcerer spell attacks.
        """
        if self.innate_sorcery_active:
            return False
        feature = self.get_feature("Innate Sorcery")
        if not feature or not feature.use():
            return False
        self.innate_sorcery_active = True
        self.innate_sorcery_rounds_remaining = 10
        return True

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

    def use_wild_shape(self) -> bool:
        feature = self.get_feature("Wild Shape")
        if not feature or not feature.use():
            return False
        self.wild_shape_rounds_remaining = 10
        if not self.wild_shape_speed_bonus_active:
            self.speed_bonus_ft += 10
            self.wild_shape_speed_bonus_active = True
        self.temp_hp = max(self.temp_hp, 6 + self.level)
        return True

    def use_monk_focus(self) -> bool:
        feature = self.get_feature("Monk's Focus")
        if not feature or not feature.use():
            return False
        self.focus_empowered_rounds = max(1, self.focus_empowered_rounds)
        return True

    def arm_smite(self) -> bool:
        if self.smite_armed:
            return False
        feature = self.get_feature("Smite")
        if not feature or not feature.use():
            return False
        self.smite_armed = True
        return True

    def use_hunters_mark(self, target) -> bool:
        """Apply Hunter's Mark to a target. Uses Favored Enemy free casts first, then feature uses."""
        # Favored Enemy (Ranger lv1): free casts before spending feature uses
        if self.favored_enemy_free_casts > 0:
            self.favored_enemy_free_casts -= 1
            self.hunters_mark_target_id = id(target)
            return True
        feature = self.get_feature("Hunter's Mark")
        if not feature or not feature.use():
            return False
        self.hunters_mark_target_id = id(target)
        return True

    def use_font_of_magic(self) -> bool:
        feature = self.get_feature("Font of Magic")
        if not feature or not feature.use():
            return False
        for slot_level in sorted(self.spell_slots_max.keys()):
            current = self.spell_slots_current.get(slot_level, 0)
            maximum = self.spell_slots_max.get(slot_level, 0)
            if current < maximum:
                self.spell_slots_current[slot_level] = current + 1
                return True
        return False

    def use_arcane_recovery(self) -> bool:
        feature = self.get_feature("Arcane Recovery")
        if not feature or not feature.use():
            return False
        max_level_recover = max(1, (self.level + 1) // 2)
        for slot_level in sorted(self.spell_slots_max.keys()):
            if slot_level > max_level_recover:
                continue
            current = self.spell_slots_current.get(slot_level, 0)
            maximum = self.spell_slots_max.get(slot_level, 0)
            if current < maximum:
                self.spell_slots_current[slot_level] = current + 1
                return True
        return False

    # ------------------------------------------------------------------
    # Martial Arts – Bonus Unarmed Strike  (SRD 5.2.1 Monk L1)
    # ------------------------------------------------------------------
    def martial_arts_strike(self, target, log_fn=None) -> str:
        """Perform a Martial Arts bonus unarmed strike against *target*.

        Uses the Martial Arts die (1d6+) and Dexterous Attacks (DEX if higher).
        Returns a combat log string.
        """
        ma_die = self.get_martial_arts_die()
        if not ma_die or not self._monk_unarmored():
            msg = f"{self.name} cannot use Martial Arts right now."
            if log_fn:
                log_fn(msg)
            return msg

        roll = self.roll_d20()
        dex_mod = self.get_ability_modifier("DEX")
        str_mod = self.get_ability_modifier("STR")
        ability_mod = max(str_mod, dex_mod)
        prof = self.get_proficiency_bonus()
        attack_penalty = self.get_attack_roll_penalty()
        total = roll + ability_mod + prof - attack_penalty

        target_ac = target.get_ac() if hasattr(target, "get_ac") else target.ac
        target_ac += getattr(target, "temp_ac_bonus", 0)

        hit = (roll == 20) or (total >= target_ac)
        if not hit:
            msg = (
                f"{self.name} Unarmed Strike: d20({roll})+{ability_mod + prof}={total} "
                f"vs AC {target_ac} -> MISS"
            )
            if log_fn:
                log_fn(msg)
            return msg

        # Iron Fist feat: reroll 1s on unarmed strike damage
        if self.has_origin_feat("Iron Fist"):
            base_ma_roll = self._roll_dice_reroll_ones(1, ma_die)
        else:
            base_ma_roll = dice.roll_dice(1, ma_die)
        dmg = base_ma_roll + ability_mod
        dmg_detail = f"1d{ma_die}({base_ma_roll})+{ability_mod}"
        crit_detail = ""
        if roll == 20:
            if self.has_origin_feat("Iron Fist"):
                crit_roll = self._roll_dice_reroll_ones(1, ma_die)
            else:
                crit_roll = dice.roll_dice(1, ma_die)
            dmg += crit_roll
            crit_detail = f" +crit 1d{ma_die}({crit_roll})"

        extra_notes: list[str] = []
        resisted = False
        if hasattr(target, "take_damage"):
            dmg, resisted = target.take_damage(dmg, damage_type="bludgeoning", source=self, log_fn=log_fn)
        else:
            target.hp -= dmg

        if resisted:
            extra_notes.append("resisted")

        notes = f" ({', '.join(extra_notes)})" if extra_notes else ""
        msg = (
            f"{self.name} Unarmed Strike: d20({roll})+{ability_mod + prof}={total} "
            f"vs AC {target_ac} -> HIT for {dmg} bludgeoning [{dmg_detail}{crit_detail}]{notes} (target HP {max(target.hp, 0)})"
        )
        if log_fn:
            log_fn(msg)
        return msg