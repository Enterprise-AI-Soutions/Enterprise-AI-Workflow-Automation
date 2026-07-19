"""Claude AI service — wraps the Anthropic SDK with graceful fallback."""

from __future__ import annotations

import json
from typing import Any, Optional

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Stub responses used when ANTHROPIC_API_KEY is not set ─────────────────────
_STUB_CHAT = (
    "👋 This is a demo response. Set ANTHROPIC_API_KEY in your .env to enable "
    "real Claude AI responses."
)
_STUB_SUMMARY = (
    "📄 Demo summary: This document discusses enterprise workflow automation. "
    "Set ANTHROPIC_API_KEY to generate real summaries."
)
_STUB_CLASSIFICATION = {"category": "demo", "confidence": 0.99, "reasoning": "Demo mode"}
_STUB_EXTRACTION = {"fields": {"demo_field": "demo_value"}, "confidence": 0.99}


class ClaudeService:
    """Provides chat, summarise, classify and extract capabilities via Claude."""

    def __init__(self) -> None:
        self._client = None
        if settings.claude_enabled:
            try:
                import anthropic  # type: ignore
                self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Claude AI enabled (model=%s)", settings.CLAUDE_MODEL)
            except ImportError:
                logger.warning("anthropic package not installed — running in demo mode")
        else:
            logger.info("ANTHROPIC_API_KEY not set — Claude running in demo mode")

    @property
    def enabled(self) -> bool:
        return self._client is not None

    # ── Chat ──────────────────────────────────────────────────────────────────

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[dict]] = None,
    ) -> str:
        if not self.enabled:
            return _STUB_CHAT

        messages: list[dict] = list(history or [])
        messages.append({"role": "user", "content": user_message})

        kwargs: dict[str, Any] = dict(
            model=settings.CLAUDE_MODEL,
            max_tokens=settings.CLAUDE_MAX_TOKENS,
            messages=messages,
        )
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self._client.messages.create(**kwargs)
        return response.content[0].text

    # ── Summarise ─────────────────────────────────────────────────────────────

    async def summarize(self, text: str, max_words: int = 150) -> str:
        if not self.enabled:
            return _STUB_SUMMARY

        prompt = (
            f"Summarise the following text in at most {max_words} words. "
            "Return only the summary, no preamble.\n\n"
            f"{text}"
        )
        return await self.chat(prompt, system_prompt="You are a concise summarisation assistant.")

    # ── Classify ──────────────────────────────────────────────────────────────

    async def classify(self, text: str, categories: list[str]) -> dict:
        if not self.enabled:
            return _STUB_CLASSIFICATION

        cats = ", ".join(categories)
        prompt = (
            f"Classify the following text into exactly one of these categories: {cats}.\n"
            "Respond with valid JSON only: "
            '{"category": "<chosen_category>", "confidence": <0-1 float>, "reasoning": "<brief reason>"}\n\n'
            f"Text:\n{text}"
        )
        raw = await self.chat(prompt, system_prompt="You are a text classification assistant. Return only valid JSON.")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"category": categories[0], "confidence": 0.5, "reasoning": "Parse error fallback"}

    # ── Extract ───────────────────────────────────────────────────────────────

    async def extract(self, text: str, fields: list[str]) -> dict:
        if not self.enabled:
            return _STUB_EXTRACTION

        field_list = ", ".join(fields)
        prompt = (
            f"Extract the following fields from the text: {field_list}.\n"
            "Respond with valid JSON only: "
            '{"fields": {<field>: <value>}, "confidence": <0-1 float>}\n\n'
            f"Text:\n{text}"
        )
        raw = await self.chat(prompt, system_prompt="You are a structured data extraction assistant. Return only valid JSON.")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"fields": {f: None for f in fields}, "confidence": 0.0}

    # ── Generate workflow steps ───────────────────────────────────────────────

    async def generate_workflow_steps(self, description: str) -> list[dict]:
        """Generate n8n-compatible workflow step suggestions from a plain-English description."""
        if not self.enabled:
            return [
                {"step": 1, "name": "Trigger", "type": "webhook", "config": {}},
                {"step": 2, "name": "Process with AI", "type": "claude", "config": {"task": "classify"}},
                {"step": 3, "name": "Store Result", "type": "airtable", "config": {}},
            ]

        prompt = (
            "You are an enterprise workflow automation expert.\n"
            f"Given this workflow description: {description}\n\n"
            "Generate a list of workflow steps as JSON array. Each step must have: "
            '{"step": <int>, "name": <str>, "type": <str>, "config": <dict>, "description": <str>}\n'
            "Valid types: webhook, schedule, gmail_trigger, gmail_send, calendar_create, "
            "drive_read, airtable_read, airtable_write, claude_chat, claude_classify, "
            "claude_extract, http_request, condition, loop.\n"
            "Return only the JSON array."
        )
        raw = await self.chat(prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []


# Singleton
claude_service = ClaudeService()
