#!/usr/bin/env bash
set -eu

connpassEventId=$1
spreadsheetId=$2

python3 download_participants_csv.py \
  https://pyconjp.connpass.com/event/${connpassEventId}/

wc -l event_${connpassEventId}_participants.csv

python3 upload_to_spreadsheet.py \
  event_${connpassEventId}_participants.csv \
  ${spreadsheetId}
