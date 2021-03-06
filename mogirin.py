from __future__ import annotations

import json
import os
import re

import discord
import gspread


def find_ticket_number(content: str) -> str | None:
    if m := re.search(r"\d+", content):
        return m.group(0)
    return None


class TicketNumberNotFound(Exception):
    ...


class TicketAlreadyCollected(Exception):
    ...


class TicketCollector:
    def __init__(self, spreadsheet_id: str):
        self.searcher = TicketSheetSearcher.from_id(spreadsheet_id)

    async def collect(
        self, ticket_number: str, member: discord.Member, role: discord.Role
    ):
        if not (ticket_cell := self.searcher.find_cell(ticket_number)):
            raise TicketNumberNotFound
        if self.searcher.query_already_collected(ticket_cell):
            raise TicketAlreadyCollected
        else:
            await RoleAttacher.attach(member, role)
            self.searcher.register_as_collected(ticket_cell)


class TicketSheetSearcher:
    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    @classmethod
    def from_id(cls, spreadsheet_id: str) -> TicketSheetSearcher:
        info = json.loads(os.getenv("SERVICE_ACCOUNT_INFO_AS_STR"))
        client = gspread.service_account_from_dict(info)
        spreadsheet = client.open_by_key(spreadsheet_id)
        return cls(spreadsheet.sheet1)

    def find_cell(self, ticket_number: str) -> gspread.Cell | None:
        return self.worksheet.find(ticket_number, in_column=1)

    def query_already_collected(
        self, ticket_number_cell: gspread.Cell
    ) -> bool:
        collection_status_cell = self.worksheet.cell(
            *self._status_cell_indice(ticket_number_cell)
        )
        return bool(collection_status_cell.value)

    def register_as_collected(self, ticket_number_cell: gspread.Cell):
        self.worksheet.update_cell(
            *self._status_cell_indice(ticket_number_cell), "✅"
        )

    @staticmethod
    def _status_cell_indice(
        ticket_number_cell: gspread.Cell,
    ) -> tuple[int, int]:
        return ticket_number_cell.row, ticket_number_cell.col + 2


class RoleAttacher:
    @staticmethod
    async def attach(member: discord.Member, role: discord.Role):
        await member.add_roles(role)
