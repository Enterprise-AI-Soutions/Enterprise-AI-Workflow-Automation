"""Google Workspace integration — Gmail, Calendar, Drive."""

from __future__ import annotations

import base64
import os
from email.mime.text import MIMEText
from typing import Any, Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Demo data ─────────────────────────────────────────────────────────────────
_DEMO_EMAILS = [
    {
        "id": "demo_msg_001",
        "subject": "Q3 Financial Report Request",
        "from": "cfo@acme.com",
        "to": "ops@acme.com",
        "snippet": "Please prepare the Q3 financial report by Friday...",
        "date": "2025-07-18T09:00:00Z",
        "labels": ["INBOX", "UNREAD"],
    },
    {
        "id": "demo_msg_002",
        "subject": "New Customer Onboarding - Globex Corp",
        "from": "sales@acme.com",
        "to": "ops@acme.com",
        "snippet": "We have a new enterprise customer, Globex Corp...",
        "date": "2025-07-17T14:30:00Z",
        "labels": ["INBOX"],
    },
]
_DEMO_EVENTS = [
    {
        "id": "demo_evt_001",
        "summary": "AI Workflow Review",
        "start": "2025-07-20T10:00:00Z",
        "end": "2025-07-20T11:00:00Z",
        "attendees": ["manager@acme.com"],
    }
]
_DEMO_FILES = [
    {"id": "demo_file_001", "name": "Q3_Report.pdf", "mimeType": "application/pdf", "size": "204800"},
    {"id": "demo_file_002", "name": "Customer_List.xlsx", "mimeType": "application/vnd.ms-excel", "size": "40960"},
]


class GoogleWorkspaceService:
    """Wraps Gmail, Calendar, and Drive APIs. Falls back to demo data when credentials are absent."""

    def __init__(self) -> None:
        self._credentials = None
        self._gmail = None
        self._calendar = None
        self._drive = None

        if settings.google_enabled:
            self._init_clients()
        else:
            logger.info("Google credentials not configured — running in demo mode")

    def _init_clients(self) -> None:
        try:
            from google.oauth2.credentials import Credentials  # type: ignore
            from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
            from google.auth.transport.requests import Request  # type: ignore
            from googleapiclient.discovery import build  # type: ignore

            SCOPES = [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/calendar",
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
                    logger.warning("Google credentials file not found — falling back to demo mode")
                    return

            self._credentials = creds
            self._gmail = build("gmail", "v1", credentials=creds)
            self._calendar = build("calendar", "v3", credentials=creds)
            self._drive = build("drive", "v3", credentials=creds)
            logger.info("Google Workspace clients initialised")

        except Exception as exc:
            logger.error("Failed to initialise Google clients: %s", exc)

    @property
    def enabled(self) -> bool:
        return self._gmail is not None

    # ── Gmail ─────────────────────────────────────────────────────────────────

    async def list_emails(self, max_results: int = 10, query: str = "") -> list[dict]:
        if not self.enabled:
            return _DEMO_EMAILS[:max_results]
        try:
            result = self._gmail.users().messages().list(
                userId="me", maxResults=max_results, q=query
            ).execute()
            messages = result.get("messages", [])
            details = []
            for msg in messages:
                detail = self._gmail.users().messages().get(
                    userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["Subject", "From", "To", "Date"]
                ).execute()
                headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
                details.append({
                    "id": msg["id"],
                    "subject": headers.get("Subject", ""),
                    "from": headers.get("From", ""),
                    "to": headers.get("To", ""),
                    "date": headers.get("Date", ""),
                    "snippet": detail.get("snippet", ""),
                    "labels": detail.get("labelIds", []),
                })
            return details
        except Exception as exc:
            logger.error("Gmail list_emails error: %s", exc)
            return _DEMO_EMAILS[:max_results]

    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> dict:
        if not self.enabled:
            return {"status": "demo", "message": f"Demo: would send email to {to}", "messageId": "demo_sent_001"}
        try:
            mime = MIMEText(body, "html" if html else "plain")
            mime["to"] = to
            mime["subject"] = subject
            raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
            result = self._gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
            return {"status": "sent", "messageId": result.get("id")}
        except Exception as exc:
            logger.error("Gmail send_email error: %s", exc)
            return {"status": "error", "message": str(exc)}

    # ── Calendar ──────────────────────────────────────────────────────────────

    async def list_events(self, max_results: int = 10, calendar_id: str = "primary") -> list[dict]:
        if not self.enabled:
            return _DEMO_EVENTS[:max_results]
        try:
            result = self._calendar.events().list(
                calendarId=calendar_id,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()
            events = result.get("items", [])
            return [
                {
                    "id": e["id"],
                    "summary": e.get("summary", ""),
                    "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
                    "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date", "")),
                    "attendees": [a["email"] for a in e.get("attendees", [])],
                }
                for e in events
            ]
        except Exception as exc:
            logger.error("Calendar list_events error: %s", exc)
            return _DEMO_EVENTS[:max_results]

    async def create_event(self, summary: str, start: str, end: str, attendees: list[str], description: str = "") -> dict:
        if not self.enabled:
            return {"status": "demo", "eventId": "demo_evt_created", "summary": summary}
        try:
            body: dict[str, Any] = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start, "timeZone": "UTC"},
                "end": {"dateTime": end, "timeZone": "UTC"},
                "attendees": [{"email": a} for a in attendees],
            }
            event = self._calendar.events().insert(calendarId="primary", body=body).execute()
            return {"status": "created", "eventId": event.get("id"), "summary": summary}
        except Exception as exc:
            logger.error("Calendar create_event error: %s", exc)
            return {"status": "error", "message": str(exc)}

    # ── Drive ─────────────────────────────────────────────────────────────────

    async def list_files(self, max_results: int = 10, query: str = "") -> list[dict]:
        if not self.enabled:
            return _DEMO_FILES[:max_results]
        try:
            result = self._drive.files().list(
                pageSize=max_results,
                q=query or None,
                fields="files(id,name,mimeType,size,modifiedTime)",
            ).execute()
            return result.get("files", [])
        except Exception as exc:
            logger.error("Drive list_files error: %s", exc)
            return _DEMO_FILES[:max_results]


# Singleton
google_service = GoogleWorkspaceService()
