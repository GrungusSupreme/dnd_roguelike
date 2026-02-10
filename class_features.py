"""Class features system based on D&D 2024 rules.

Each class has unique abilities and features that affect gameplay.
This module defines the base features for each class.
"""


class ClassFeature:
    """Represents a single class feature with usage and cooldown management."""
    
    def __init__(
        self,
        name: str,
        description: str,
        max_uses: int | None = 1,
        recharge: str = "rest",  # "rest", "combat", or "unlimited"
        effect_type: str = "passive",  # "passive", "action", "bonus_action", "reaction"
    ):
        """
        Initialize a class feature.
        
        Args:
            name: Feature name (e.g., "Rage", "Sneak Attack")
            description: What the feature does
            max_uses: Number of uses per recharge period. None means unlimited (passive features).
            recharge: When uses refresh ("rest", "combat", "unlimited")
            effect_type: How the feature is used in combat
        """
        self.name = name
        self.description = description
        self.max_uses = max_uses
        self.uses_remaining = max_uses if max_uses is not None else float('inf')
        self.recharge = recharge
        self.effect_type = effect_type
    
    def use(self) -> bool:
        """Use the feature if available. Returns True if successful."""
        if self.max_uses is None:  # Passive features always available
            return True
        if self.uses_remaining > 0:
            self.uses_remaining -= 1
            return True
        return False
    
    def restore(self) -> None:
        """Restore all uses of the feature."""
        if self.max_uses is not None:
            self.uses_remaining = self.max_uses
        else:
            self.uses_remaining = float('inf')
    
    def __repr__(self) -> str:
        if self.max_uses is None:
            return f"{self.name} [Passive]"
        return f"{self.name} ({int(self.uses_remaining)}/{self.max_uses})"


# Class feature definitions
CLASS_FEATURES = {
    "Artificer": [
        ClassFeature(
            name="Tinker's Magic",
            description="Cast spells using INT modifier. Can mend objects or create magical effects.",
            max_uses=2,
            recharge="rest",
            effect_type="action",
        ),
    ],
    "Barbarian": [
        ClassFeature(
            name="Rage",
            description="Enter a state of fury for 1 minute. Gain resistance to physical damage and +2 damage to melee attacks.",
            max_uses=2,
            recharge="rest",
            effect_type="bonus_action",
        ),
    ],
    "Bard": [
        ClassFeature(
            name="Bardic Inspiration",
            description="Grant an ally a d6 bonus to their next attack, ability check, or saving throw.",
            max_uses=3,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Expertise",
            description="Double proficiency bonus on 2 chosen skills. Increases to 4 skills at level 9.",
            max_uses=None,  # Always active
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Cleric": [
        ClassFeature(
            name="Channel Divinity",
            description="Use divine power to turn undead or heal. 2 uses per long rest.",
            max_uses=2,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Healing Light",
            description="Bonus action to heal an ally for 1d4 + WIS modifier.",
            max_uses=3,
            recharge="rest",
            effect_type="bonus_action",
        ),
    ],
    "Druid": [
        ClassFeature(
            name="Wild Shape",
            description="Transform into a beast form with improved AC and HP. Uses recharge on short rest.",
            max_uses=2,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Druidic",
            description="Understand and speak Druidic language. Read secret messages left by other druids.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Fighter": [
        ClassFeature(
            name="Action Surge",
            description="Take an additional action on your turn. Use once per short rest.",
            max_uses=1,
            recharge="rest",
            effect_type="bonus_action",
        ),
        ClassFeature(
            name="Second Wind",
            description="Bonus action to heal yourself for 1d10 + Fighter level.",
            max_uses=1,
            recharge="rest",
            effect_type="bonus_action",
        ),
        ClassFeature(
            name="Fighting Style",
            description="Gain a fighting style (Archery, Defense, Dueling, Great Weapon Fighting, or Two-Weapon Fighting).",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Monk": [
        ClassFeature(
            name="Martial Arts",
            description="Unarmed strikes deal 1d6 damage and can be used as bonus actions. Scales with level.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Unarmored Defense",
            description="AC equals 10 + DEX modifier + WIS modifier when wearing no armor.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Monk's Focus",
            description="Energy system for special abilities. Spend Focus to perform stunning strikes or movement.",
            max_uses=3,
            recharge="rest",
            effect_type="bonus_action",
        ),
    ],
    "Paladin": [
        ClassFeature(
            name="Lay On Hands",
            description="Healing pool equal to 5 × your level. Touch to heal in any amount.",
            max_uses=None,  # Limited by pool, not uses
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Smite",
            description="Expend a spell slot to add 2d6 radiant damage to your next melee attack.",
            max_uses=2,  # At level 1, typically
            recharge="rest",
            effect_type="passive",
        ),
        ClassFeature(
            name="Divine Sense",
            description="Sense the presence of celestials, fiends, and undead within 60 feet.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Ranger": [
        ClassFeature(
            name="Favored Enemy",
            description="Bonus damage (1d4) against a chosen enemy type. Gain advantage on checks to track them.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Hunter's Mark",
            description="Mark a target to deal an extra 1d4 damage. Bonus action to switch marks.",
            max_uses=2,
            recharge="rest",
            effect_type="bonus_action",
        ),
        ClassFeature(
            name="Expertise",
            description="Double proficiency bonus on Perception and Survival checks (or 2 chosen skills).",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Rogue": [
        ClassFeature(
            name="Sneak Attack",
            description="Deal an extra 1d6 damage (scales to 10d6) when using a finesse weapon and advantageous position.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Cunning Action",
            description="Bonus action to Dash, Disengage, or Hide on each turn.",
            max_uses=None,
            recharge="passive",
            effect_type="bonus_action",
        ),
        ClassFeature(
            name="Expertise",
            description="Double proficiency bonus on 2 chosen skills. Increases at level 6, 9, etc.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Uncanny Dodge",
            description="Reaction to halve damage from an attack you can see.",
            max_uses=1,
            recharge="rest",
            effect_type="reaction",
        ),
    ],
    "Sorcerer": [
        ClassFeature(
            name="Innate Sorcery",
            description="Cast spells without material components. 2 uses per long rest.",
            max_uses=2,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Font of Magic",
            description="Convert spell slots to Sorcery Points or vice versa. Spend 1 point for flexibility.",
            max_uses=3,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Metamagic",
            description="Modify spellcasting with options like Twinned Spell, Quickened Spell, etc.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
    "Warlock": [
        ClassFeature(
            name="Eldritch Invocations",
            description="Gain otherworldly invocations at level 1. Examples: Agonizing Blast, One with Shadows.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Pact Magic",
            description="Use Charisma for spellcasting. Regain spell slots on short rest.",
            max_uses=2,
            recharge="rest",
            effect_type="passive",
        ),
    ],
    "Wizard": [
        ClassFeature(
            name="Spellcasting",
            description="Prepare spells from the Wizard spell list. Intelligence is your spellcasting ability.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
        ClassFeature(
            name="Arcane Recovery",
            description="Recover spell slots totaling up to half your Wizard level on a short rest.",
            max_uses=1,
            recharge="rest",
            effect_type="action",
        ),
        ClassFeature(
            name="Ritual Casting",
            description="Cast prepared spells as rituals without using spell slots.",
            max_uses=None,
            recharge="passive",
            effect_type="passive",
        ),
    ],
}


def get_class_features(class_name: str) -> list:
    """Get a list of ClassFeature objects for a given class.
    
    Args:
        class_name: Name of the class (must match CLASS_FEATURES keys).
        
    Returns:
        List of ClassFeature objects, or empty list if class not found.
    """
    return [ClassFeature(f.name, f.description, f.max_uses, f.recharge, f.effect_type)
            for f in CLASS_FEATURES.get(class_name, [])]


def get_class_feature_summaries(class_name: str) -> str:
    """Get a formatted string of class features for display.
    
    Args:
        class_name: Name of the class.
        
    Returns:
        Formatted string suitable for display in UI.
    """
    features = CLASS_FEATURES.get(class_name, [])
    if not features:
        return "No special features."
    
    summary = []
    for feature in features:
        if feature.max_uses is None:
            uses_str = "[Passive]"
        elif feature.max_uses == 1:
            uses_str = f"[{feature.recharge.title()} - 1 use]"
        else:
            uses_str = f"[{feature.recharge.title()} - {feature.max_uses} uses]"
        summary.append(f"• {feature.name} {uses_str}: {feature.description}")
    
    return "\n".join(summary)
