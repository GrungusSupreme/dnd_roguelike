import time
import argparse
import random
from character import Character
from creator import create_character_interactive
from waves import spawn_wave
from class_definitions import generate_level_1_stats
import dice
from colors import Colors, success, error, warning, info, player_action, enemy_action, header, divider, bold

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

	enemy_distances = {
		e: max(2, getattr(e, "attack_range", 1) + 1)
		for e in enemies
	}

	for actor, _, _, _ in combatants:
		auto_features = actor is not player
		for message in actor.start_combat(auto_features=auto_features):
			if actor is player:
				print(info(message))

	round_num = 0
	while player.is_alive() and any(e.is_alive() for e in enemies):
		round_num += 1
		print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'█'*50}{Colors.RESET}")
		print(f"{Colors.BOLD}{Colors.MAGENTA}  ROUND {round_num}{Colors.RESET}")
		print(f"{Colors.BOLD}{Colors.MAGENTA}{'█'*50}{Colors.RESET}")
		for actor, init, raw, is_player in combatants:
			if not actor.is_alive():
				continue
			actor.start_turn()
			if is_player:
				# player turn: interactive choice or auto-attack first alive
				if interactive:
					# list alive enemies
					alive = [e for e in enemies if e.is_alive()]
					if not alive:
						break
					remaining_actions = 1
					while remaining_actions > 0:
						# Display player status and enemy list
						print("\n" + "="*50)
						print(f"{Colors.BLUE}{Colors.BOLD}[YOUR TURN]{Colors.RESET} HP: {player.hp}/{player.max_hp} | AC: {player.ac} | Gold: {player.gold} | Potions: {player.potions}")
						print("="*50)
						print(f"\n{Colors.YELLOW}Enemies in combat:{Colors.RESET}")
						for idx, e in enumerate(alive, start=1):
							hp_bar = "█" * (e.hp // 5) + "░" * ((e.max_hp - e.hp) // 5)
							distance = enemy_distances.get(e, 1)
							print(f"  {idx}. {e.name:12} [{hp_bar}] HP {e.hp}/{e.max_hp} | Dist {distance}")
						
						print(f"\n{Colors.CYAN}--- Actions ---{Colors.RESET}")
						print("  (1-9)  Attack enemy (by number)")
						print("  (h)    Use healing potion")
						print("  (d)    Defend (+2 AC this round)")
						print("  (f)    Use class feature")
						print("  (s)    Show detailed stats")
						print("  (q)    Quit combat")
						
						if msvcrt and single_key_mode:
							choice = msvcrt.getwch().strip().lower()
							print()
						else:
							choice = input(f"\n{Colors.BLUE}> Choose action:{Colors.RESET} ").strip().lower()

						if choice == "q":
							print(error("You quit the combat."))
							return False
						if choice == "s":
							print(f"\n{bold('[STATS]')} Level {player.level} | HP {player.hp}/{player.max_hp} | AC {player.ac}")
							print(f"        Attack Bonus: +{player.attack_bonus} | Damage: {player.dmg_num}d{player.dmg_die}+{player.dmg_bonus}")
							print(f"        Gold: {player.gold} | XP: {player.xp}/{100*player.level} to next level")
							continue
						if choice == "h":
							healed = player.use_potion()
							if healed:
								print(success(f"You use a potion and heal {healed} HP (now {player.hp}/{player.max_hp}). Potions left: {player.potions}"))
							else:
								print(error("No potions left!"))
							remaining_actions -= 1
							continue
						if choice == "d":
							player.defend(ac_bonus=2)
							print(success("You brace for incoming attacks (+2 AC this round)."))
							remaining_actions -= 1
							continue
						if choice == "f":
							available = player.get_available_features()
							if not available:
								print(error("No features available."))
								continue
							print("\nAvailable features:")
							for idx, feature in enumerate(available, start=1):
								uses = "Passive" if feature.max_uses is None else f"{int(feature.uses_remaining)}/{feature.max_uses}"
								print(f"  {idx}. {feature.name} [{uses}]")
							choice_raw = input("Choose a feature number (or press Enter to cancel): ").strip()
							if not choice_raw:
								continue
							if not choice_raw.isdigit():
								print(warning("Invalid choice."))
								continue
							idx = int(choice_raw) - 1
							if idx < 0 or idx >= len(available):
								print(warning("Invalid choice."))
								continue
							feature = available[idx]
							if feature.name == "Rage":
								if player.activate_rage():
									print(success("You enter a Rage!"))
								else:
									print(error("Rage not available."))
								continue
							elif feature.name == "Second Wind":
								healed = player.use_second_wind()
								if healed:
									print(success(f"Second Wind heals {healed} HP (now {player.hp}/{player.max_hp})."))
								else:
									print(error("Second Wind not available."))
								continue
							elif feature.name == "Bardic Inspiration":
								if player.use_bardic_inspiration():
									print(success("You inspire yourself. Next attack gains +1d6."))
								else:
									print(error("Bardic Inspiration not available."))
								continue
							elif feature.name == "Channel Divinity":
								healed = player.use_channel_divinity()
								if healed:
									print(success(f"Channel Divinity heals {healed} HP (now {player.hp}/{player.max_hp})."))
								else:
									print(error("Channel Divinity not available."))
								continue
							elif feature.name == "Lay On Hands":
								amount_raw = input(f"Spend how many HP? (pool {player.lay_on_hands_pool}): ").strip()
								if not amount_raw.isdigit():
									print(warning("Invalid amount."))
									continue
								healed = player.use_lay_on_hands(int(amount_raw))
								if healed:
									print(success(f"Lay On Hands heals {healed} HP (pool {player.lay_on_hands_pool})."))
								else:
									print(error("Lay On Hands not available."))
								continue
							elif feature.name == "Action Surge":
								if feature.use():
									remaining_actions += 1
									print(success("Action Surge! You gain one extra action this turn."))
									continue
								else:
									print(error("Action Surge not available."))
									continue
							else:
								print(warning("Feature not implemented yet."))
								continue
							action_type = "bonus_action" if feature.effect_type == "bonus_action" else "action"
							if action_type == "action":
								remaining_actions -= 1
							continue
						if choice.isdigit():
							idx = int(choice) - 1
							if 0 <= idx < len(alive):
								target = alive[idx]
								distance = enemy_distances.get(target, 1)
								if distance > player.attack_range:
									print(warning(f"Target out of range (Dist {distance}, Range {player.attack_range})."))
									continue
								pre_alive = target.is_alive()
								actor.attack(target)
								# if we killed an enemy, award bounty
								if pre_alive and not target.is_alive() and getattr(target, "bounty", 0) > 0:
									actor.gold += target.bounty
									print(success(f"{target.name} defeated! You loot {target.bounty} gold (total {actor.gold})."))
									# small chance to drop an item (potion)
									drop_roll = dice.roll_die(100)
									if drop_roll <= 30:
										from items import create_potion_of_healing

										potion = create_potion_of_healing()
										actor.add_item(potion)
										print(info(f"{target.name} dropped a Potion! ({actor.potions} potions now)"))
									# award XP on kill (simple: bounty * 10)
									xp_gain = getattr(target, "bounty", 0) * 10
									if xp_gain > 0:
										levels = actor.add_xp(xp_gain)
										print(info(f"You gain {xp_gain} XP (level {actor.level})."))
								else:
									print(player_action(f"You attack {target.name}."))
								remaining_actions -= 1
								continue
						print(warning("Invalid choice, try again."))
					if not any(e.is_alive() for e in enemies):
						print("\n" + "="*50)
						print(f"{Colors.GREEN}{Colors.BOLD}All enemies defeated! You win this round!{Colors.RESET}")
						print("="*50)
						return True
				else:
					# auto-attack first alive enemy
					target = next((e for e in enemies if e.is_alive() and enemy_distances.get(e, 1) <= player.attack_range), None)
					if target is None:
						print(player_action(f"No enemies in range (Range {player.attack_range})."))
						continue
					pre_alive = target.is_alive()
					actor.attack(target)
					if pre_alive and not target.is_alive() and getattr(target, "bounty", 0) > 0:
						actor.gold += target.bounty
						print(f"You loot {target.bounty} gold (total {actor.gold}).")
						# small chance to drop an item (potion)
						drop_roll = dice.roll_die(100)
						if drop_roll <= 30:
							from items import create_potion_of_healing

							potion = create_potion_of_healing()
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
					distance = enemy_distances.get(actor, 1)
					if distance > actor.attack_range:
						enemy_distances[actor] = max(1, distance - 1)
						print(enemy_action(f"  {actor.name} advances (distance {enemy_distances[actor]})."))
						continue
					# enemy behavior
					beh = getattr(actor, "behavior", None)
					if beh == "healer":
						# find lowest HP alive ally (excluding self)
						allies = [a for a in enemies if a.is_alive() and a is not actor]
						if allies:
							target = min(allies, key=lambda x: x.hp)
							healed = actor.heal_ally(target, 7)
							if healed:
								print(enemy_action(f"  {actor.name} heals {target.name} for {healed} HP."))
							else:
								# fallback: attack player if no potion
								actor.attack(player)
								print(enemy_action(f"  {actor.name} attacks you!"))
						else:
							actor.attack(player)
							print(enemy_action(f"  {actor.name} attacks you!"))
					else:
						actor.attack(player)
						print(enemy_action(f"  {actor.name} attacks you!"))
					if not player.is_alive():
						print("\n" + "="*50)
						print(error("You have been slain."))
						print("="*50)
						return False
		if not no_delay:
			time.sleep(0.4)
		# clear temporary AC bonuses at end of round
		for a, _, _, _ in combatants:
			if hasattr(a, "temp_ac_bonus"):
				a.temp_ac_bonus = 0
			for message in a.end_round():
				if a is player:
					print(info(message))
		
		# brief round summary
		alive_enemies = [e for e in enemies if e.is_alive()]
		if alive_enemies and player.is_alive():
			print(f"\n{Colors.DIM}[Round {round_num} End] Player HP: {player.hp}/{player.max_hp} | Enemies: {len(alive_enemies)} remaining{Colors.RESET}")
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
	default_stats = generate_level_1_stats("Fighter")
	player = Character(
		"Player",
		hp=default_stats["hp"],
		ac=default_stats["ac"],
		attack_bonus=default_stats["attack_bonus"],
		dmg_num=default_stats["dmg_num"],
		dmg_die=default_stats["dmg_die"],
		dmg_bonus=default_stats["dmg_bonus"],
		initiative_bonus=default_stats["initiative_bonus"],
		class_name="Fighter",
		ability_scores=default_stats["ability_scores"],
		gold=50,
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
		print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*50}{Colors.RESET}")
		print(f"{Colors.BOLD}{Colors.CYAN}  WAVE {wave}{Colors.RESET}")
		print(f"{Colors.BOLD}{Colors.CYAN}{'═'*50}{Colors.RESET}")
		enemies = spawn_wave(wave)
		survived = run_combat(player, enemies, interactive=interactive_mode)
		if not survived:
			print(f"\n{error(f'Game Over - You survived {wave-1} waves.')}")
			break
	else:
		print(f"\n{Colors.GREEN}{Colors.BOLD}🏆 VICTORY! You survived all {args.waves} waves!{Colors.RESET}")
