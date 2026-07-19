"""Google Sheets integration service."""

from __future__ import annotations

from typing import Any, Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Demo data ─────────────────────────────────────────────────────────────────
_DEMO_SPREADSHEET = {
    "spreadsheetId": "demo_spreadsheet_001",
    "properties": {"title": "Demo Spreadsheet", "locale": "en_US"},
    "sheets": [
        {"properties": {"sheetId": 0, "title": "Sheet1", "index": 0}},
        {"properties": {"sheetId": 1, "title": "Leads", "index": 1}},
    ],
    "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/demo_spreadsheet_001/edit",
}

_DEMO_VALUES = [
    ["Name", "Email", "Company", "Status", "Revenue"],
    ["Alice Johnson", "alice@acme.com", "Acme Corp", "Active", "$50,000"],
    ["Bob Smith", "bob@globex.com", "Globex Ltd", "Lead", "$0"],
    ["Carol White", "carol@initech.com", "Initech", "Closed", "$120,000"],
]

_DEMO_SHEETS_LIST = [
    {"spreadsheetId": "demo_spreadsheet_001", "title": "CRM Dashboard", "url": "https://docs.google.com/spreadsheets/d/demo_001"},
    {"spreadsheetId": "demo_spreadsheet_002", "title": "Invoice Tracker", "url": "https://docs.google.com/spreadsheets/d/demo_002"},
    {"spreadsheetId": "demo_spreadsheet_003", "title": "Workflow Logs", "url": "https://docs.google.com/spreadsheets/d/demo_003"},
]


class GoogleSheetsService:
    """Wraps the Google Sheets API v4. Falls back to demo data when credentials are absent."""

    def __init__(self) -> None:
        self._service = None
        self._drive_service = None

        if settings.google_enabled:
            self._init_clients()
        else:
            logger.info("Google credentials not configured — Sheets running in demo mode")

    def _init_clients(self) -> None:
        try:
            import os
            from google.oauth2.credentials import Credentials  # type: ignore
            from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
            from google.auth.transport.requests import Request  # type: ignore
            from googleapiclient.discovery import build  # type: ignore

            SCOPES = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly",
            ]

            creds = None
            token_file = settings.GOOGLE_TOKEN_FILE or "token.json"

            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif settings.GOOGLE_CREDENTIALS_FILE and os.path.exists(settings.GOOGLE_CREDENTIALS_FILE):
                    flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE_CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open(token_file, "w") as t:
                        t.write(creds.to_json())
                else:
                    logger.warning("Google credentials file not found — Sheets falling back to demo mode")
                    return

            self._service = build("sheets", "v4", credentials=creds)
            self._drive_service = build("drive", "v3", credentials=creds)
            logger.info("Google Sheets client initialised")

        except Exception as exc:
            logger.error("Failed to initialise Google Sheets client: %s", exc)

    @property
    def enabled(self) -> bool:
        return self._service is not None

    # ── Spreadsheet metadata ──────────────────────────────────────────────────

    async def get_spreadsheet(self, spreadsheet_id: str) -> dict:
        """Get spreadsheet metadata, including all sheet names."""
        if not self.enabled:
            return _DEMO_SPREADSHEET
        try:
            return (
                self._service.spreadsheets()
                .get(spreadsheetId=spreadsheet_id)
                .execute()
            )
        except Exception as exc:
            logger.error("Sheets get_spreadsheet error: %s", exc)
            return _DEMO_SPREADSHEET

    async def list_spreadsheets(self, max_results: int = 20) -> list[dict]:
        """List spreadsheets from Google Drive."""
        if not self.enabled:
            return _DEMO_SHEETS_LIST[:max_results]
        try:
            result = self._drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=max_results,
                fields="files(id,name,webViewLink,modifiedTime)",
            ).execute()
            return [
                {"spreadsheetId": f["id"], "title": f["name"], "url": f.get("webViewLink", ""), "modifiedTime": f.get("modifiedTime")}
                for f in result.get("files", [])
            ]
        except Exception as exc:
            logger.error("Sheets list_spreadsheets error: %s", exc)
            return _DEMO_SHEETS_LIST[:max_results]

    async def create_spreadsheet(self, title: str, sheet_names: Optional[list[str]] = None) -> dict:
        """Create a new spreadsheet."""
        if not self.enabled:
            return {
                "spreadsheetId": f"demo_new_{title.lower().replace(' ', '_')}",
                "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/demo_new/edit",
                "title": title,
                "status": "demo",
            }
        try:
            body: dict[str, Any] = {"properties": {"title": title}}
            if sheet_names:
                body["sheets"] = [{"properties": {"title": name}} for name in sheet_names]

            result = self._service.spreadsheets().create(body=body).execute()
            return {
                "spreadsheetId": result["spreadsheetId"],
                "spreadsheetUrl": result["spreadsheetUrl"],
                "title": title,
                "status": "created",
            }
        except Exception as exc:
            logger.error("Sheets create_spreadsheet error: %s", exc)
            return {"status": "error", "message": str(exc)}

    # ── Reading values ────────────────────────────────────────────────────────

    async def read_values(
        self,
        spreadsheet_id: str,
        range_notation: str = "Sheet1",
        value_render_option: str = "FORMATTED_VALUE",
    ) -> dict:
        """Read values from a range (e.g. 'Sheet1!A1:E10')."""
        if not self.enabled:
            return {
                "spreadsheetId": spreadsheet_id,
                "range": range_notation,
                "values": _DEMO_VALUES,
                "majorDimension": "ROWS",
                "demo_mode": True,
            }
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueRenderOption=value_render_option,
                )
                .execute()
            )
            return {
                "spreadsheetId": spreadsheet_id,
                "range": result.get("range", range_notation),
                "values": result.get("values", []),
                "majorDimension": result.get("majorDimension", "ROWS"),
            }
        except Exception as exc:
            logger.error("Sheets read_values error: %s", exc)
            return {"spreadsheetId": spreadsheet_id, "range": range_notation, "values": [], "error": str(exc)}

    async def batch_read(self, spreadsheet_id: str, ranges: list[str]) -> list[dict]:
        """Read multiple ranges at once."""
        if not self.enabled:
            return [
                {"range": r, "values": _DEMO_VALUES[:2], "demo_mode": True}
                for r in ranges
            ]
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .batchGet(spreadsheetId=spreadsheet_id, ranges=ranges)
                .execute()
            )
            return [
                {"range": vr.get("range", ""), "values": vr.get("values", [])}
                for vr in result.get("valueRanges", [])
            ]
        except Exception as exc:
            logger.error("Sheets batch_read error: %s", exc)
            return []

    # ── Writing values ────────────────────────────────────────────────────────

    async def write_values(
        self,
        spreadsheet_id: str,
        range_notation: str,
        values: list[list[Any]],
        value_input_option: str = "USER_ENTERED",
    ) -> dict:
        """Overwrite values in a range."""
        if not self.enabled:
            return {
                "spreadsheetId": spreadsheet_id,
                "updatedRange": range_notation,
                "updatedRows": len(values),
                "updatedColumns": max((len(r) for r in values), default=0),
                "updatedCells": sum(len(r) for r in values),
                "status": "demo",
            }
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueInputOption=value_input_option,
                    body={"values": values},
                )
                .execute()
            )
            return {
                "spreadsheetId": result.get("spreadsheetId"),
                "updatedRange": result.get("updatedRange"),
                "updatedRows": result.get("updatedRows", 0),
                "updatedColumns": result.get("updatedColumns", 0),
                "updatedCells": result.get("updatedCells", 0),
            }
        except Exception as exc:
            logger.error("Sheets write_values error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def append_rows(
        self,
        spreadsheet_id: str,
        range_notation: str,
        values: list[list[Any]],
        value_input_option: str = "USER_ENTERED",
    ) -> dict:
        """Append rows to the end of a table."""
        if not self.enabled:
            return {
                "spreadsheetId": spreadsheet_id,
                "tableRange": range_notation,
                "updates": {
                    "updatedRows": len(values),
                    "updatedCells": sum(len(r) for r in values),
                },
                "status": "demo",
            }
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_notation,
                    valueInputOption=value_input_option,
                    insertDataOption="INSERT_ROWS",
                    body={"values": values},
                )
                .execute()
            )
            return {
                "spreadsheetId": result.get("spreadsheetId"),
                "tableRange": result.get("tableRange"),
                "updates": result.get("updates", {}),
            }
        except Exception as exc:
            logger.error("Sheets append_rows error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def clear_range(self, spreadsheet_id: str, range_notation: str) -> dict:
        """Clear values in a range (keeps formatting)."""
        if not self.enabled:
            return {"spreadsheetId": spreadsheet_id, "clearedRange": range_notation, "status": "demo"}
        try:
            result = (
                self._service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_notation, body={})
                .execute()
            )
            return {
                "spreadsheetId": result.get("spreadsheetId"),
                "clearedRange": result.get("clearedRange"),
            }
        except Exception as exc:
            logger.error("Sheets clear_range error: %s", exc)
            return {"status": "error", "message": str(exc)}

    # ── Formatting & batch updates ────────────────────────────────────────────

    async def batch_update(self, spreadsheet_id: str, requests: list[dict]) -> dict:
        """Send arbitrary Sheets batchUpdate requests (formatting, merges, etc.)."""
        if not self.enabled:
            return {"spreadsheetId": spreadsheet_id, "replies": [], "status": "demo", "requests_count": len(requests)}
        try:
            result = (
                self._service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests})
                .execute()
            )
            return {
                "spreadsheetId": result.get("spreadsheetId"),
                "replies": result.get("replies", []),
            }
        except Exception as exc:
            logger.error("Sheets batch_update error: %s", exc)
            return {"status": "error", "message": str(exc)}

    async def add_sheet(self, spreadsheet_id: str, sheet_title: str) -> dict:
        """Add a new sheet tab to an existing spreadsheet."""
        request = {"addSheet": {"properties": {"title": sheet_title}}}
        result = await self.batch_update(spreadsheet_id, [request])
        return result

    async def format_header_row(self, spreadsheet_id: str, sheet_id: int = 0) -> dict:
        """Apply bold + background colour to the first row (header)."""
        requests = [
            {
                "repeatCell": {
                    "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)",
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": 1}},
                    "fields": "gridProperties.frozenRowCount",
                }
            },
        ]
        return await self.batch_update(spreadsheet_id, requests)


# Singleton
google_sheets_service = GoogleSheetsService()
