from unittest import TestCase
from unittest.mock import MagicMock, patch

import gspread

import mogirin as m


class FromIdTicketSheetSearcherTestCase(TestCase):
    @patch("mogirin.gspread.service_account_from_dict")
    @patch("mogirin.json.loads")
    @patch("mogirin.os.getenv")
    def test_from_id(self, getenv, json_loads, service_account_from_dict):
        spreadsheet_id = "1**some_spreadsheet_id**"
        client = service_account_from_dict.return_value
        spreadsheet = client.open_by_key.return_value

        actual = m.TicketSheetSearcher.from_id(spreadsheet_id)

        self.assertIsInstance(actual, m.TicketSheetSearcher)
        self.assertEqual(actual.worksheet, spreadsheet.sheet1)
        getenv.assert_called_once_with("SERVICE_ACCOUNT_INFO_AS_STR")
        json_loads.assert_called_once_with(getenv.return_value)
        service_account_from_dict.assert_called_once_with(
            json_loads.return_value
        )
        client.open_by_key.assert_called_once_with(spreadsheet_id)


class FindCellTicketSheetSearcherTestCase(TestCase):
    def test_find_cell(self):
        worksheet = MagicMock(spec=gspread.Worksheet)
        sut = m.TicketSheetSearcher(worksheet)
        ticket_number = "123456"

        actual = sut.find_cell(ticket_number)

        self.assertEqual(actual, worksheet.find.return_value)
        worksheet.find.assert_called_once_with(ticket_number, in_column=1)
