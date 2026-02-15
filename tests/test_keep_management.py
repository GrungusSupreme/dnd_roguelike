import unittest

from keep_management import KeepState


class TestKeepManagement(unittest.TestCase):
    def test_raid_day_advances_date_and_updates_resources(self):
        keep = KeepState(day=1, month_index=0, food=10, supplies=5, morale=5)
        messages = keep.advance_raid_day(wave_number=2, survived=True)

        self.assertEqual(keep.day, 2)
        self.assertEqual(keep.food, 8)
        self.assertEqual(keep.supplies, 7)
        self.assertEqual(keep.morale, 6)
        self.assertTrue(any("Raid repelled" in message for message in messages))

    def test_month_rollover(self):
        keep = KeepState(day=30, month_index=0, food=10, supplies=5, morale=5)
        keep.advance_raid_day(wave_number=1, survived=True)

        self.assertEqual(keep.day, 1)
        self.assertEqual(keep.month_index, 1)


if __name__ == "__main__":
    unittest.main()
