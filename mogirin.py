from __future__ import annotations

import json
import os

import discord
import gspread


class TicketCollector:
    def __init__(self, spreadsheet_id: str):
        self.searcher = SpreadsheetSearcher(spreadsheet_id)

    async def collect(
        self, ticket_number: str, member: discord.Member, role: discord.Role
    ) -> str:
        # TODO: 例外を送出するだけにしてメッセージはbot側で設定したい
        if ticket_cell := self.searcher.find_cell(ticket_number):
            is_collected = self.searcher.query_already_collected(ticket_cell)
            if is_collected:
                return (
                    f"RuntimeError: the ticket {ticket_number!r} "
                    "is already used."
                )
            else:
                await RoleAttacher.attach(member, role)
                self.searcher.register_as_collected(ticket_cell)
                return "Accepted! Welcome to PyCon JP 2021 venue!"
        return (
            f"RuntimeError: Couldn't find your number {ticket_number!r}.\n"
            "Sorry, try again."
        )


class SpreadsheetSearcher:
    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    @classmethod
    def from_id(cls, spreadsheet_id: str) -> SpreadsheetSearcher:
        info = json.loads(os.getenv("SERVICE_ACCOUNT_INFO_AS_STR"))
        client = gspread.service_account_from_dict(info)
        spreadsheet = client.open_by_key(spreadsheet_id)
        return cls(spreadsheet.sheet1)

    def find_cell(self, ticket_number: str) -> gspread.Cell | None:
        return self.worksheet.find(ticket_number, in_column=1)

    def query_already_collected(self, cell: gspread.Cell) -> bool:
        collection_status_cell = self.worksheet.cell(cell.row, cell.col + 2)
        return bool(collection_status_cell.value)

    def register_as_collected(self, cell: gspread.Cell):
        self.worksheet.update_cell(cell.row, cell.col + 2, "✅")


class RoleAttacher:
    @staticmethod
    async def attach(member: discord.Member, role: discord.Role):
        await member.add_roles(role)
