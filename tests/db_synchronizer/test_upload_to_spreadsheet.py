from unittest import TestCase

from db_synchronizer.upload_to_spreadsheet import difference


class DifferenceTestCase(TestCase):
    def test_sheet_is_empty(self):
        participants = [(2, "a"), (3, "b"), (7, "d")]
        records = []

        actual = difference(participants, records)

        expected = [(2, "a"), (3, "b"), (7, "d")]
        self.assertEqual(actual, expected)

    def test_sheet_records_are_continuous(self):
        participants = [(2, "a"), (3, "b"), (5, "c"), (7, "d")]
        records = [
            {
                "receipt_number": 2,
                "display_name": "a",
                "collected": "",
                "type": "スタッフ",
            },
            {
                "receipt_number": 3,
                "display_name": "b",
                "collected": "✅",
                "type": "スタッフ",
            },
            {
                "receipt_number": 5,
                "display_name": "c",
                "collected": "",
                "type": "スタッフ",
            },
        ]

        actual = difference(participants, records)

        expected = [(7, "d")]
        self.assertEqual(actual, expected)
