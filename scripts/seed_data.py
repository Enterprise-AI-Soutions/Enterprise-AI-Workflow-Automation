"""
seed_data.py — Seed the database with sample workflows for development.

Usage:
    python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.database.session import AsyncSessionFactory, engine
from app.services.database.base import Base
from app.services.workflow.workflow_service import WorkflowService
import app.models  # noqa: F401


SAMPLE_WORKFLOWS = [
    {
        "name": "Email Triage — Sales",
        "description": "Classify incoming emails and route sales inquiries to CRM",
        "status": "active",
        "trigger_type": "email",
        "tags": ["email", "sales", "ai"],
        "steps": [
            {"step": 1, "name": "Gmail Trigger", "type": "gmail_trigger", "config": {"label": "INBOX"}},
            {"step": 2, "name": "Claude Classify", "type": "claude_classify", "config": {"categories": ["Sales", "Support", "Other"]}},
            {"step": 3, "name": "Route", "type": "condition", "config": {}},
            {"step": 4, "name": "Airtable CRM", "type": "airtable_write", "config": {"table": "Leads"}},
        ],
    },
    {
        "name": "Invoice Processing",
        "description": "Extract invoice fields with AI and log to Airtable",
        "status": "active",
        "trigger_type": "webhook",
        "tags": ["finance", "invoice", "ai"],
        "steps": [
            {"step": 1, "name": "Webhook Trigger", "type": "webhook", "config": {"path": "invoice-upload"}},
            {"step": 2, "name": "Claude Extract", "type": "claude_extract", "config": {"fields": ["invoice_number", "vendor", "amount", "due_date"]}},
            {"step": 3, "name": "Airtable Log", "type": "airtable_write", "config": {"table": "Invoices"}},
            {"step": 4, "name": "Notify Finance", "type": "gmail_send", "config": {"to": "finance@company.com"}},
        ],
    },
    {
        "name": "Meeting Scheduler",
        "description": "Parse meeting requests and auto-create Google Calendar events",
        "status": "draft",
        "trigger_type": "webhook",
        "tags": ["calendar", "scheduling"],
        "steps": [
            {"step": 1, "name": "Webhook", "type": "webhook", "config": {}},
            {"step": 2, "name": "Claude Parse", "type": "claude_extract", "config": {"fields": ["title", "date", "attendees"]}},
            {"step": 3, "name": "Create Event", "type": "calendar_create", "config": {}},
            {"step": 4, "name": "Send Confirmation", "type": "gmail_send", "config": {}},
        ],
    },
    {
        "name": "Engineering Doc Summariser",
        "description": "Summarise new Google Drive docs and post to Slack",
        "status": "inactive",
        "trigger_type": "event",
        "tags": ["engineering", "docs", "google-drive"],
        "steps": [
            {"step": 1, "name": "Drive Trigger", "type": "drive_read", "config": {"folder": "RFCs"}},
            {"step": 2, "name": "Claude Summarise", "type": "claude_chat", "config": {"max_words": 200}},
            {"step": 3, "name": "Post Summary", "type": "http_request", "config": {"url": "https://hooks.slack.com/..."}},
        ],
    },
]


async def seed():
    print("🌱 Seeding database with sample workflows...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    service = WorkflowService()
    async with AsyncSessionFactory() as db:
        for wf_data in SAMPLE_WORKFLOWS:
            wf = await service.create_workflow(db, wf_data)
            print(f"  ✅ Created: {wf.name} ({wf.id})")
        await db.commit()

    print(f"\n✨ Seeded {len(SAMPLE_WORKFLOWS)} workflows successfully!")
    print("Run `uvicorn app.main:app --reload` and visit http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(seed())
