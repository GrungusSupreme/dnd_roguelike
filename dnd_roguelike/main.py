import time
import argparse
import random
from character import Character
from creator import create_character_interactive
from waves import spawn_wave
import dice

try:
	import msvcrt
except Exception:
	msvcrt = None

# defaults used when module imported in tests
single_key_mode = False
no_delay = False


def run_combat(player, enemies, interactive=False):
	"""Run a combat using initiative order among combatants.

	`enemies` should be a list of `Character`.
	This function runs rounds until the player or all enemies are defeated.
	If `interactive` is True, the player's turns will prompt for input to
	choose which enemy to attack.
	Returns True if the player survived the combat, False if the player died
	or quit.
	"""
	# roll initiative for all combatants: store (actor, total, raw_roll, is_player)
	combatants = []
	p_total, p_roll = player.roll_initiative()
	combatants.append((player, p_total, p_roll, True))
	for e in enemies:
		e_total, e_roll = e.roll_initiative()
		combatants.append((e, e_total, e_roll, False))

	# compute final ordering with tie-breakers
	combatants = compute_initiative_order(combatants)

	round_num = 0
	while player.is_alive() and any(e.is_alive() for e in enemies):
		round_num += 1
		print(f"\n-- Round {round_num} --")
		for actor, init, raw, is_player in combatants:
			if not actor.is_alive():
				continue
			if is_player:
				# player turn: interactive choice or auto-attack first alive
				if interactive:
					# list alive enemies
					alive = [e for e in enemies if e.is_alive()]
					if not alive:
						break
					while True:
						print("Your turn. Enemies:")
						for idx, e in enumerate(alive, start=1):
							print(f"  {idx}. {e.name} (HP {e.hp})")
						if msvcrt and single_key_mode:
							print("Press a number to attack, 'a' to attack, 'h' heal, 'd' defend, 's' stats, 'q' quit (single-key):", end=" ", flush=True)
							ch = msvcrt.getwch()
							print(ch)
							choice = ch.strip().lower()
						else:
							choice = input("Choose enemy number to attack, 'a' attack, 'h' heal, 'd' defend, 's' stats, 'q' quit: ").strip().lower()

						if choice == "q":
							print("You quit the combat.")
							return False
						if choice == "s":
							print(f"Player HP: {player.hp}, AC: {player.ac}")
							continue
						if choice == "h" or choice == "heal":
							healed = player.use_potion(8)
							if healed:
								print(f"You use a potion and heal {healed} HP (HP {player.hp}). Potions left: {player.potions}")
							else:
								print("No potions left!")
							break
						if choice == "d" or choice == "defend":
							player.defend(ac_bonus=2)
							print("You brace for incoming attacks (+2 AC this round).")
							break
						if choice.isdigit():
							idx = int(choice) - 1
							if 0 <= idx < len(alive):
								target = alive[idx]
								pre_alive = target.is_alive()
								actor.attack(target)
								# if we killed an enemy, award bounty
								if pre_alive and not target.is_alive() and getattr(target, "bounty", 0) > 0:
									actor.gold += target.bounty
									print(f"You loot {target.bounty} gold (total {actor.gold}).")
									# small chance to drop an item (potion)
									drop_roll = dice.roll_die(100)
									if drop_roll <= 30:
										from items import Item

										potion = Item("Potion", "potion", value=8)
										actor.add_item(potion)
										print(f"{target.name} dropped a Potion! ({actor.potions} potions now)")
									# award XP on kill (simple: bounty * 10)
									xp_gain = getattr(target, "bounty", 0) * 10
									if xp_gain > 0:
										levels = actor.add_xp(xp_gain)
										print(f"{actor.name} gains {xp_gain} XP (level {actor.level}, xp {actor.xp}).")
								break
						print("Invalid choice, try again.")
					if not any(e.is_alive() for e in enemies):
						print("All enemies defeated! You win.")
						return True
				else:
					# auto-attack first alive enemy
					target = next((e for e in enemies if e.is_alive()), None)
					if target is None:
						break
					pre_alive = target.is_alive()
					actor.attack(target)
					if pre_alive and not target.is_alive() and getattr(target, "bounty", 0) > 0:
						actor.gold += target.bounty
						print(f"You loot {target.bounty} gold (total {actor.gold}).")
						# small chance to drop an item (potion)
						drop_roll = dice.roll_die(100)
						if drop_roll <= 30:
							from items import Item

							potion = Item("Potion", "potion", value=8)
							actor.add_item(potion)
							print(f"{target.name} dropped a Potion! ({actor.potions} potions now)")
						# award XP on kill (simple: bounty * 10)
						xp_gain = getattr(target, "bounty", 0) * 10
						if xp_gain > 0:
							levels = actor.add_xp(xp_gain)
							print(f"{actor.name} gains {xp_gain} XP (level {actor.level}, xp {actor.xp}).")
					if not any(e.is_alive() for e in enemies):
						print("All enemies defeated! You win.")
						return True
			else:
				# enemy attacks player
				if player.is_alive():
					# enemy behavior
					beh = getattr(actor, "behavior", None)
					if beh == "healer":
						# find lowest HP alive ally (excluding self)
						allies = [a for a in enemies if a.is_alive() and a is not actor]
						if allies:
							target = min(allies, key=lambda x: x.hp)
							healed = actor.heal_ally(target, 6)
							if healed:
								print(f"{actor.name} heals {target.name} for {healed} HP (potions left: {actor.potions}).")
							else:
								# fallback: attack player if no potion
								actor.attack(player)
						else:
							actor.attack(player)
					else:
						actor.attack(player)
					if not player.is_alive():
						print("You have been slain.")
						return False
		if not no_delay:
			time.sleep(0.4)
		# clear temporary AC bonuses at end of round
		for a, _, _, _ in combatants:
			if hasattr(a, "temp_ac_bonus"):
				a.temp_ac_bonus = 0
	return player.is_alive()


def compute_initiative_order(combatants):
	"""Given a list of `(actor, total, raw_roll, is_player)`, return a new
	list ordered by initiative with tie-breakers resolved via extra d20 rolls.

	Tie-breaking rule: for any group with equal `total`, roll `dice.roll_die()`
	once per tied actor and sort by that roll (desc). This is simple and
	testable.
	"""
	# initial sort by total descending
	combatants_sorted = sorted(combatants, key=lambda t: t[1], reverse=True)

	# find tied groups and resolve them
	i = 0
	result = []
	while i < len(combatants_sorted):
		group = [combatants_sorted[i]]
		j = i + 1
		while j < len(combatants_sorted) and combatants_sorted[j][1] == combatants_sorted[i][1]:
			group.append(combatants_sorted[j])
			j += 1

		if len(group) == 1:
			result.append(group[0])
		else:
			# roll tie-breakers for each actor in the group
			tb = []
			for actor, total, raw, is_player in group:
				tbr = dice.roll_die()
				tb.append((actor, total, raw, is_player, tbr))
			tb_sorted = sorted(tb, key=lambda t: t[4], reverse=True)
			# append without the tie-break value
			for actor, total, raw, is_player, tbr in tb_sorted:
				result.append((actor, total, raw, is_player))

		i = j

	return result


if __name__ == "__main__":
	print("Starting wave survival demo: Player vs waves of goblins (initiative)")
	player = Character(
		"Player",
		hp=30,
		ac=15,
		attack_bonus=5,
		dmg_num=1,
		dmg_die=8,
		dmg_bonus=3,
		initiative_bonus=2,
	)

	parser = argparse.ArgumentParser(description="dnd_roguelike demo")
	parser.add_argument("--interactive", "-i", action="store_true", help="Prompt for choices each player turn")
	parser.add_argument("--single-key", action="store_true", help="Use single-key input for choices (Windows only)")
	parser.add_argument("--seed", type=int, help="Seed RNG for reproducible runs")
	parser.add_argument("--waves", type=int, default=3, help="Number of waves to run")
	parser.add_argument("--no-delay", action="store_true", help="Skip delays between rounds")
	parser.add_argument("--create-character", action="store_true", help="Run interactive character creator before starting")
	args = parser.parse_args()

	if args.seed is not None:
		random.seed(args.seed)

	interactive_mode = args.interactive
	single_key_mode = args.single_key and (msvcrt is not None)
	no_delay = args.no_delay

	# optionally run the interactive creator
	if args.create_character:
		player = create_character_interactive()
	else:
		player = player

	for wave in range(1, args.waves + 1):
		print(f"\n=== Wave {wave} ===")
		enemies = spawn_wave(wave)
		survived = run_combat(player, enemies, interactive=interactive_mode)
		if not survived:
			print(f"You survived {wave-1} waves.")
			break
	else:
		print(f"You survived all {args.waves} waves! Victory!")
