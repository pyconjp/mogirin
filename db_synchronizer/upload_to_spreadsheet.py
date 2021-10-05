import argparse
import csv
import re
import sys

import gspread

CONNPASS_TYPE_MAP = {"221241": "一般", "224112": "スタッフ", "224510": "スポンサー"}


def difference(participants, records):
    if not records:
        return participants
    registered_receipt_number_set = {r["receipt_number"] for r in records}
    return [
        p for p in participants if p[0] not in registered_receipt_number_set
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("participants_csv")
    parser.add_argument("spreadsheet_key")
    parser.add_argument("--service_account", required=True)
    args = parser.parse_args()

    m = re.search(r"\d+", args.participants_csv)
    event_id = m.group(0)
    ticket_type = CONNPASS_TYPE_MAP[event_id]

    with open(args.participants_csv, encoding="cp932") as f:
        reader = csv.DictReader(f)
        participants = [
            (int(d["受付番号"]), d["表示名"]) for d in reader if d["参加ステータス"] == "参加"
        ]
    participants.sort(key=lambda t: t[0])

    client = gspread.service_account(filename=args.service_account)
    spreadsheet = client.open_by_key(args.spreadsheet_key)
    worksheet = spreadsheet.sheet1
    records = worksheet.get_all_records()
    filtered_by_type = [r for r in records if r["type"] == ticket_type]

    need_to_append_participants = difference(participants, filtered_by_type)

    if not need_to_append_participants:
        print("No need to append to spreadsheet.")
        sys.exit()

    rows = [
        (str(p[0]), p[1], None, ticket_type)
        for p in need_to_append_participants
    ]
    worksheet.append_rows(rows)
