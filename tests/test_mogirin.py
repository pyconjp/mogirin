import asyncio
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import gspread

import mogirin as m


class InitTicketCollectorTestCase(TestCase):
    @patch("mogirin.TicketSheetSearcher.from_id")
    def test_init(self, from_id):
        spreadsheet_id = "1**some_spreadsheet_id*1"

        actual = m.TicketCollector(spreadsheet_id)

        self.assertEqual(actual.searcher, from_id.return_value)
        from_id.assert_called_once_with(spreadsheet_id)


@patch("mogirin.RoleAttacher.attach", new_callable=AsyncMock)
@patch("mogirin.TicketSheetSearcher.from_id")
class CollectTicketCollectorTestCase(TestCase):
    def setUp(self):
        self.spreadsheet_id = "1**some_spreadsheet_id*a"

        self.member = MagicMock(spec=discord.Member)
        self.role = MagicMock(spec=discord.Role)

    def test_normal_case(self, from_id, attach):
        spreadsheet_id = "1**some_spreadsheet_id*a"
        sut = m.TicketCollector(spreadsheet_id)
        searcher = from_id.return_value
        ticket_cell = gspread.Cell(50, 1, "678901")
        searcher.find_cell.return_value = ticket_cell
        searcher.query_already_collected.return_value = False

        ticket_number = "678901"
        member = MagicMock(spec=discord.Member)
        role = MagicMock(spec=discord.Role)

        asyncio.run(sut.collect(ticket_number, member, role))

        searcher.find_cell.assert_called_once_with("678901")
        searcher.query_already_collected.assert_called_once_with(ticket_cell)
        attach.assert_awaited_once_with(member, role)
        searcher.register_as_collected.assert_called_once_with(ticket_cell)

    def test_ticket_already_collected(self, from_id, attach):
        sut = m.TicketCollector(self.spreadsheet_id)
        searcher = from_id.return_value
        ticket_cell = gspread.Cell(69, 1, "679018")
        searcher.find_cell.return_value = ticket_cell
        searcher.query_already_collected.return_value = True
        ticket_number = "679018"

        asyncio.run(sut.collect(ticket_number, self.member, self.role))

        searcher.find_cell.assert_called_once_with("679018")
        searcher.query_already_collected.assert_called_once_with(ticket_cell)
        attach.assert_not_awaited()
        searcher.register_as_collected.assert_not_called()


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


class QueryAlreadyCollectedTicketSheetSearcherTestCase(TestCase):
    def setUp(self):
        self.worksheet = MagicMock(spec=gspread.Worksheet)
        self.sut = m.TicketSheetSearcher(self.worksheet)

    def test_return_true(self):
        cell = gspread.Cell(2, 1, "345678")
        self.worksheet.cell.return_value = gspread.Cell(2, 3, "✅")

        actual = self.sut.query_already_collected(cell)

        self.assertTrue(actual)
        self.worksheet.cell.assert_called_once_with(2, 3)

    def test_return_false(self):
        cell = gspread.Cell(3, 1, "345679")
        self.worksheet.cell.return_value = gspread.Cell(3, 3, "")

        actual = self.sut.query_already_collected(cell)

        self.assertFalse(actual)
        self.worksheet.cell.assert_called_once_with(3, 3)


class RegisterAsCollectedTicketSheetSearcherTestCase(TestCase):
    def test_register_as_collected(self):
        worksheet = MagicMock(spec=gspread.Worksheet)
        sut = m.TicketSheetSearcher(worksheet)
        cell = gspread.Cell(4, 1, "567890")

        sut.register_as_collected(cell)

        worksheet.update_cell.assert_called_once_with(4, 3, "✅")


class AttachRoleAttacherTestCase(TestCase):
    def test_attach(self):
        member = AsyncMock(spec=discord.Member)
        role = MagicMock(spec=discord.Role)

        asyncio.run(m.RoleAttacher.attach(member, role))

        member.add_roles.assert_awaited_once_with(role)
