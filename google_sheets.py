import os
import json
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def _load_service_account_credentials():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Prefer JSON content from env var for hosted environments.
    json_content = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if json_content:
        creds_dict = json.loads(json_content)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    # Legacy: base64-encoded JSON
    json_b64 = os.environ.get("GOOGLE_CREDENTIALS_JSON_BASE64")
    if json_b64:
        creds_dict = json.loads(base64.b64decode(json_b64).decode("utf-8"))
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    keyfile_path = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    return ServiceAccountCredentials.from_json_keyfile_name(keyfile_path, scope)


def connect_sheet():
    creds = _load_service_account_credentials()
    client = gspread.authorize(creds)
    sheet = client.open("Kingdom Workforce Workers").sheet1
    return sheet


def append_worker_to_sheet(worker_data):
    sheet = connect_sheet()
    sheet.append_row(worker_data)
