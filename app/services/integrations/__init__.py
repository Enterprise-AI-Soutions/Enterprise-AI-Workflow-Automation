"""Integrations package."""

from app.services.integrations.google_workspace import GoogleWorkspaceService, google_service
from app.services.integrations.airtable import AirtableService, airtable_service
from app.services.integrations.n8n import N8NService, n8n_service

__all__ = [
    "GoogleWorkspaceService", "google_service",
    "AirtableService", "airtable_service",
    "N8NService", "n8n_service",
]
