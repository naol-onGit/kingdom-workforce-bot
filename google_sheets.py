import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Kingdom Workforce Workers").sheet1
    return sheet


def append_worker_to_sheet(worker_data):
    sheet = connect_sheet()
    sheet.append_row(worker_data)