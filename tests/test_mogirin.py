from unittest import TestCase
from unittest.mock import patch

import mogirin as m


class FromIdSpreadsheetSearcherTestCase(TestCase):
    @patch("mogirin.gspread.service_account_from_dict")
    @patch("mogirin.json.loads")
    @patch("mogirin.os.getenv")
    def test_from_id(self, getenv, json_loads, service_account_from_dict):
        spreadsheet_id = "1**some_spreadsheet_id**"
        client = service_account_from_dict.return_value
        spreadsheet = client.open_by_key.return_value

        actual = m.SpreadsheetSearcher.from_id(spreadsheet_id)

        self.assertIsInstance(actual, m.SpreadsheetSearcher)
        self.assertEqual(actual.worksheet, spreadsheet.sheet1)
        getenv.assert_called_once_with("SERVICE_ACCOUNT_INFO_AS_STR")
        json_loads.assert_called_once_with(getenv.return_value)
        service_account_from_dict.assert_called_once_with(
            json_loads.return_value
        )
        client.open_by_key.assert_called_once_with(spreadsheet_id)
