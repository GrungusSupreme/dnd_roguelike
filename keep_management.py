"""Lightweight keep management and calendar loop for Phase 3 slice 1."""

from dataclasses import dataclass


MONTH_NAMES = [
    "Hammer",
    "Alturiak",
    "Ches",
    "Tarsakh",
    "Mirtul",
    "Kythorn",
    "Flamerule",
    "Eleasis",
    "Eleint",
    "Marpenoth",
    "Uktar",
    "Nightal",
]


@dataclass
class KeepState:
    day: int = 1
    month_index: int = 0
    days_in_month: int = 30
    food: int = 40
    supplies: int = 20
    morale: int = 5

    def month_name(self) -> str:
        return MONTH_NAMES[self.month_index % len(MONTH_NAMES)]

    def status_line(self) -> str:
        return (
            f"Date {self.month_name()} {self.day} | "
            f"Food {self.food} | Supplies {self.supplies} | Morale {self.morale}"
        )

    def _next_day(self) -> None:
        self.day += 1
        if self.day > self.days_in_month:
            self.day = 1
            self.month_index = (self.month_index + 1) % len(MONTH_NAMES)

    def advance_raid_day(self, wave_number: int, survived: bool = True) -> list[str]:
        """Advance one day for a raid and apply simple keep economy changes."""
        messages: list[str] = []

        # Daily upkeep
        food_cost = 2
        self.food = max(0, self.food - food_cost)
        messages.append(f"Keep consumes {food_cost} food.")

        # Raid outcome resource changes
        if survived:
            supply_gain = max(1, wave_number)
            self.supplies += supply_gain
            self.morale = min(10, self.morale + 1)
            messages.append(f"Raid repelled: +{supply_gain} supplies, morale +1.")
        else:
            self.supplies = max(0, self.supplies - 2)
            self.morale = max(0, self.morale - 2)
            messages.append("Raid setback: -2 supplies, morale -2.")

        # Starvation pressure
        if self.food == 0:
            self.morale = max(0, self.morale - 1)
            messages.append("Food stores are empty. Morale drops by 1.")

        self._next_day()
        messages.append(f"New date: {self.month_name()} {self.day}.")
        return messages
