"""Simple dice utilities for dnd_roguelike."""
import random


def roll_die(sides=20):
    return random.randint(1, sides)


def roll_dice(num, sides):
    return sum(random.randint(1, sides) for _ in range(num))
