"""Health check router."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.ai import claude_service
from app.services.integrations import google_service, airtable_service, n8n_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Application health check")
async def health_check():
    """Returns the health status of the application and all integrations."""
    return JSONResponse({
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "integrations": {
            "claude_ai": {
                "enabled": claude_service.enabled,
                "model": settings.CLAUDE_MODEL if claude_service.enabled else None,
                "status": "connected" if claude_service.enabled else "demo_mode",
            },
            "google_workspace": {
                "enabled": google_service.enabled,
                "status": "connected" if google_service.enabled else "demo_mode",
            },
            "airtable": {
                "enabled": airtable_service.enabled,
                "status": "connected" if airtable_service.enabled else "demo_mode",
            },
            "n8n": {
                "enabled": n8n_service.enabled,
                "base_url": settings.N8N_BASE_URL,
                "status": "connected" if n8n_service.enabled else "demo_mode",
            },
        },
    })


@router.get("/ping", summary="Simple ping")
async def ping():
    return {"ping": "pong"}
