"""Lightweight keep management and calendar loop for Phase 3 slice 1."""

import random
from dataclasses import dataclass
from dataclasses import field


SEASON_NAMES = ["Spring", "Summer", "Winter", "Fall"]
SEASON_LENGTH_DAYS = 25
SEASONS_PER_YEAR = 4
DAYS_PER_YEAR = SEASON_LENGTH_DAYS * SEASONS_PER_YEAR


@dataclass
class KeepState:
    day: int = 1
    year: int = 1
    month_index: int = 0
    days_in_month: int = SEASON_LENGTH_DAYS
    food: int = 100
    supplies: int = 20
    morale: int = 5
    food_storage_cap: int = 500
    farmland_production_per_day: int = 50
    season_raid_schedule: dict[int, int] = field(default_factory=dict)
    season_raid_player_level: int = 1
    _year_rollover_pending: bool = False
    _season_schedule_pending: bool = True

    def __post_init__(self) -> None:
        self.month_index = int(self.month_index) % len(SEASON_NAMES)
        self.day = max(1, min(int(self.day), self.days_in_month))
        self.year = max(1, int(self.year))

    @property
    def season_index(self) -> int:
        return self.month_index

    @season_index.setter
    def season_index(self, value: int) -> None:
        self.month_index = value % len(SEASON_NAMES)

    def season_name(self) -> str:
        return SEASON_NAMES[self.month_index % len(SEASON_NAMES)]

    def month_name(self) -> str:
        return self.season_name()

    def status_line(self) -> str:
        return f"Date Year {self.year}, {self.season_name()} {self.day}"

    def day_of_year(self) -> int:
        return (self.month_index * self.days_in_month) + self.day

    def days_per_year(self) -> int:
        return DAYS_PER_YEAR

    def consume_year_rollover(self) -> bool:
        if not self._year_rollover_pending:
            return False
        self._year_rollover_pending = False
        return True

    def consume_year_end_level_up_trigger(self) -> bool:
        """Return True once when a year rollover has just occurred.

        This is the seasonal-loop hook point for any year-end progression
        (for example level-up processing) owned by higher-level game systems.
        """
        return self.consume_year_rollover()

    def generate_season_raid_schedule(self, player_level: int, rng: random.Random | None = None) -> dict[int, int]:
        """Generate random raid counts per day for the current season.

        Rules:
        - total raids: 10 × player level
        - daily cap: 2 × player level
        - distributed randomly across the 25 season days
        """
        level = max(1, int(player_level))
        total_raids = 10 * level
        per_day_cap = 2 * level
        picker = rng or random
        schedule = {day: 0 for day in range(1, self.days_in_month + 1)}
        candidate_days = list(schedule.keys())

        raids_left = total_raids
        while raids_left > 0:
            open_days = [day for day in candidate_days if schedule[day] < per_day_cap]
            if not open_days:
                break
            chosen_day = picker.choice(open_days)
            schedule[chosen_day] += 1
            raids_left -= 1

        self.season_raid_schedule = {day: count for day, count in schedule.items() if count > 0}
        self.season_raid_player_level = level
        self._season_schedule_pending = False
        return dict(self.season_raid_schedule)

    def ensure_season_raid_schedule(self, player_level: int) -> bool:
        """Generate a new season raid schedule if one is pending."""
        if not self._season_schedule_pending:
            return False
        self.generate_season_raid_schedule(player_level=player_level)
        return True

    def raids_scheduled_today(self) -> int:
        return int(self.season_raid_schedule.get(self.day, 0))

    def _next_day(self) -> None:
        self.day += 1
        if self.day > self.days_in_month:
            self.day = 1
            self.month_index = (self.month_index + 1) % len(SEASON_NAMES)
            self.season_raid_schedule = {}
            self._season_schedule_pending = True
            if self.month_index == 0:
                self.year += 1
                self._year_rollover_pending = True

    def advance_raid_day(self, wave_number: int, survived: bool = True) -> list[str]:
        """Advance one day for a raid and apply simple keep economy changes."""
        messages: list[str] = []

        produced_food = self.farmland_production_per_day
        pre_food = self.food
        self.food = min(self.food_storage_cap, self.food + produced_food)
        gained_food = self.food - pre_food
        if gained_food > 0:
            messages.append(f"Farmland produces {gained_food} food.")

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
        messages.append(f"New date: Year {self.year}, {self.month_name()} {self.day}.")
        if self._year_rollover_pending:
            messages.append(f"A new year begins (Year {self.year}).")
        return messages
