from unittest import TestCase

from db_synchronizer.upload_to_spreadsheet import difference


class DifferenceTestCase(TestCase):
    def test_sheet_is_empty(self):
        participants = [(2, "a"), (3, "b"), (7, "d")]
        records = []

        actual = difference(participants, records)

        expected = [(2, "a"), (3, "b"), (7, "d")]
        self.assertEqual(actual, expected)
