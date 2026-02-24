import unittest
import random

from keep_management import DAYS_PER_YEAR, KeepState, SEASON_LENGTH_DAYS


class TestKeepManagement(unittest.TestCase):
    def test_raid_day_advances_date_and_updates_resources(self):
        keep = KeepState(day=1, month_index=0, food=10, supplies=5, morale=5)
        messages = keep.advance_raid_day(wave_number=2, survived=True)

        self.assertEqual(keep.day, 2)
        self.assertEqual(keep.food, 58)
        self.assertEqual(keep.supplies, 7)
        self.assertEqual(keep.morale, 6)
        self.assertTrue(any("Farmland produces" in message for message in messages))
        self.assertTrue(any("Raid repelled" in message for message in messages))

    def test_season_rollover(self):
        keep = KeepState(day=25, month_index=0, year=1, food=10, supplies=5, morale=5)
        keep.advance_raid_day(wave_number=1, survived=True)

        self.assertEqual(keep.day, 1)
        self.assertEqual(keep.month_index, 1)
        self.assertEqual(keep.year, 1)

    def test_year_rollover_sets_hook_flag(self):
        keep = KeepState(day=25, month_index=3, year=1)
        keep.advance_raid_day(wave_number=1, survived=True)

        self.assertEqual(keep.day, 1)
        self.assertEqual(keep.month_index, 0)
        self.assertEqual(keep.year, 2)
        self.assertTrue(keep.consume_year_end_level_up_trigger())
        self.assertFalse(keep.consume_year_end_level_up_trigger())

    def test_calendar_constants_and_day_of_year(self):
        keep = KeepState(day=1, month_index=0, year=1)
        self.assertEqual(keep.days_in_month, SEASON_LENGTH_DAYS)
        self.assertEqual(keep.days_per_year(), DAYS_PER_YEAR)
        self.assertEqual(keep.day_of_year(), 1)

        keep.month_index = 3
        keep.day = 25
        self.assertEqual(keep.day_of_year(), 100)

    def test_generate_season_raid_schedule_respects_total_and_daily_cap(self):
        keep = KeepState(day=1, month_index=0, year=1)
        schedule = keep.generate_season_raid_schedule(player_level=2, rng=random.Random(7))

        self.assertEqual(sum(schedule.values()), 20)
        self.assertTrue(all(1 <= day <= 25 for day in schedule.keys()))
        self.assertTrue(all(count <= 4 for count in schedule.values()))

    def test_ensure_season_schedule_on_rollover(self):
        keep = KeepState(day=25, month_index=0, year=1)
        keep.generate_season_raid_schedule(player_level=1, rng=random.Random(11))

        keep.advance_raid_day(wave_number=1, survived=True)
        self.assertEqual(keep.day, 1)
        self.assertEqual(keep.month_index, 1)
        self.assertEqual(keep.season_raid_schedule, {})

        regenerated = keep.ensure_season_raid_schedule(player_level=3)
        self.assertTrue(regenerated)
        self.assertEqual(sum(keep.season_raid_schedule.values()), 30)
        self.assertEqual(keep.season_raid_player_level, 3)


if __name__ == "__main__":
    unittest.main()
