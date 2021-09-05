import json
import os

import gspread


class TicketCollector:
    def __init__(self, spreadsheet_id):
        info = json.loads(os.getenv("SERVICE_ACCOUNT_INFO_AS_STR"))
        client = gspread.service_account_from_dict(info)
        spreadsheet = client.open_by_key(spreadsheet_id)
        self.worksheet = spreadsheet.sheet1

    def collect(self, ticket_number: str) -> str:
        # TODO: 例外を送出するだけにしてメッセージはbot側で設定したい
        if cell := self.worksheet.find(ticket_number, in_column=1):
            collected_status = self.worksheet.cell(cell.row, cell.col + 2)
            if collected_status.value:
                return (
                    f"RuntimeError: the ticket {ticket_number!r} "
                    "is already used."
                )
            else:
                self.worksheet.update_cell(cell.row, cell.col + 2, "✅")
                return "Accepted! Welcome to PyCon JP 2021 venue!"
        return (
            f"RuntimeError: Couldn't find your number {ticket_number!r}.\n"
            "Sorry, try again."
        )
