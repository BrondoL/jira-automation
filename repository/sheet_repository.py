from typing import List

import gspread
from google.oauth2.service_account import Credentials

from model import sheet


class GoogleSheetRepositoryRepository():
    def __init__(self, credential_file, sheet_id):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = Credentials.from_service_account_file(
            credential_file,
            scopes=scopes
        )

        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def get_all_responses(self) -> List[sheet.GoogleSheetResponse]:
        records = self.sheet.get_all_records()
        return [
            sheet.GoogleSheetResponse(
                id=str(i + 1),  # Using row number as ID
                data=record
            ) for i, record in enumerate(records)
        ]

    def delete_all_responses(self) -> bool:
        try:
            # Keep the header row (row 1) and clear everything else
            header = self.sheet.row_values(1)
            self.sheet.clear()
            self.sheet.update('A1', [header])
            return True
        except Exception:
            return False