"""Claude AI endpoints."""

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.ai import claude_service

router = APIRouter(prefix="/ai", tags=["AI — Claude"])


# ── Request / Response schemas ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt to guide Claude")
    history: Optional[List[dict]] = Field(None, description="Previous messages [{role, content}]")

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to summarise")
    max_words: int = Field(150, ge=20, le=500)

class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1)
    categories: List[str] = Field(..., min_length=2, description="Possible categories")

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    fields: List[str] = Field(..., min_length=1, description="Fields to extract from the text")

class GenerateWorkflowRequest(BaseModel):
    description: str = Field(..., min_length=10, description="Plain-English workflow description")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/chat", summary="Chat with Claude AI")
async def chat(request: ChatRequest):
    response = await claude_service.chat(
        user_message=request.message,
        system_prompt=request.system_prompt,
        history=request.history,
    )
    return {
        "response": response,
        "model": claude_service._client and claude_service._client.__class__.__name__,
        "demo_mode": not claude_service.enabled,
    }


@router.post("/summarize", summary="Summarise text")
async def summarize(request: SummarizeRequest):
    summary = await claude_service.summarize(request.text, max_words=request.max_words)
    return {"summary": summary, "demo_mode": not claude_service.enabled}


@router.post("/classify", summary="Classify text into categories")
async def classify(request: ClassifyRequest):
    result = await claude_service.classify(request.text, categories=request.categories)
    return {**result, "demo_mode": not claude_service.enabled}


@router.post("/extract", summary="Extract structured fields from text")
async def extract(request: ExtractRequest):
    result = await claude_service.extract(request.text, fields=request.fields)
    return {**result, "demo_mode": not claude_service.enabled}


@router.post("/generate-workflow", summary="Generate workflow steps from description")
async def generate_workflow(request: GenerateWorkflowRequest):
    steps = await claude_service.generate_workflow_steps(request.description)
    return {
        "description": request.description,
        "steps": steps,
        "step_count": len(steps),
        "demo_mode": not claude_service.enabled,
    }


@router.get("/status", summary="Claude AI service status")
async def ai_status():
    return {
        "enabled": claude_service.enabled,
        "model": claude_service._client and "claude" or None,
        "configured_model": claude_service._client and "configured" or "demo_mode",
        "demo_mode": not claude_service.enabled,
    }
