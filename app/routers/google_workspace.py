"""Google Workspace router — Gmail, Calendar, Drive."""

from typing import List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.integrations import google_service

router = APIRouter(prefix="/google", tags=["Google Workspace"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class SendEmailRequest(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    html: bool = Field(False, description="Send as HTML email")


class CreateEventRequest(BaseModel):
    summary: str = Field(..., min_length=1)
    start: str = Field(..., description="ISO 8601 datetime, e.g. 2025-07-20T10:00:00Z")
    end: str = Field(..., description="ISO 8601 datetime, e.g. 2025-07-20T11:00:00Z")
    attendees: List[str] = Field(default_factory=list)
    description: str = Field("", description="Event description")


# ── Gmail ─────────────────────────────────────────────────────────────────────

@router.get("/gmail/messages", summary="List Gmail messages")
async def list_gmail_messages(
    max_results: int = Query(10, ge=1, le=50),
    query: str = Query("", description="Gmail search query, e.g. 'is:unread'"),
):
    messages = await google_service.list_emails(max_results=max_results, query=query)
    return {
        "messages": messages,
        "count": len(messages),
        "demo_mode": not google_service.enabled,
    }


@router.post("/gmail/send", summary="Send an email via Gmail")
async def send_email(request: SendEmailRequest):
    result = await google_service.send_email(
        to=request.to, subject=request.subject, body=request.body, html=request.html
    )
    return {**result, "demo_mode": not google_service.enabled}


# ── Calendar ──────────────────────────────────────────────────────────────────

@router.get("/calendar/events", summary="List Calendar events")
async def list_calendar_events(
    max_results: int = Query(10, ge=1, le=50),
    calendar_id: str = Query("primary"),
):
    events = await google_service.list_events(max_results=max_results, calendar_id=calendar_id)
    return {
        "events": events,
        "count": len(events),
        "demo_mode": not google_service.enabled,
    }


@router.post("/calendar/events", summary="Create a Calendar event")
async def create_calendar_event(request: CreateEventRequest):
    result = await google_service.create_event(
        summary=request.summary,
        start=request.start,
        end=request.end,
        attendees=request.attendees,
        description=request.description,
    )
    return {**result, "demo_mode": not google_service.enabled}


# ── Drive ─────────────────────────────────────────────────────────────────────

@router.get("/drive/files", summary="List Google Drive files")
async def list_drive_files(
    max_results: int = Query(10, ge=1, le=50),
    query: str = Query("", description="Drive search query"),
):
    files = await google_service.list_files(max_results=max_results, query=query)
    return {
        "files": files,
        "count": len(files),
        "demo_mode": not google_service.enabled,
    }


@router.get("/status", summary="Google Workspace integration status")
async def google_status():
    return {"enabled": google_service.enabled, "demo_mode": not google_service.enabled}
