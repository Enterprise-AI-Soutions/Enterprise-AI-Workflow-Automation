# Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enterprise AI Workflow Platform               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│   │  Gmail   │    │ Calendar │    │  Drive   │    │ Airtable │  │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│        │               │               │               │         │
│   ─────┴───────────────┴───────────────┴───────────────┴──────  │
│                            API Layer                             │
│   ─────────────────────────────────────────────────────────────  │
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                    FastAPI Backend                       │    │
│   │                                                          │    │
│   │  /api/v1/                                                │    │
│   │  ├── /health          → Health & status                 │    │
│   │  ├── /workflows       → CRUD + execution                │    │
│   │  ├── /executions      → History + logs                  │    │
│   │  ├── /ai              → Claude AI endpoints             │    │
│   │  ├── /google          → Gmail, Calendar, Drive          │    │
│   │  ├── /airtable        → Records CRUD                    │    │
│   │  └── /n8n             → Workflow engine                 │    │
│   └─────────────────────────────────────────────────────────┘    │
│                          │            │                           │
│               ┌──────────┘            └──────────┐               │
│          ┌────▼─────┐            ┌────────────────▼────────┐     │
│          │ SQLite / │            │    Claude AI (Anthropic) │     │
│          │ Postgres │            └─────────────────────────┘     │
│          └──────────┘                                            │
│                                                                   │
│   ┌─────────────────────────────────────────────────────────┐    │
│   │                      n8n Engine                          │    │
│   │  email_triage.json  /  invoice_processing.json           │    │
│   │  meeting_scheduler.json                                  │    │
│   └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Graceful Degradation
Every integration checks for its API key at startup. If absent, it operates in **demo mode** — returning realistic stub data so the application runs without any credentials configured.

### 2. Async First
The entire stack uses Python `async/await`: FastAPI, SQLAlchemy async, httpx, and the Anthropic async client. This ensures high concurrency for workflow orchestration.

### 3. Separation of Concerns
- **Routers** — HTTP interface only
- **Services** — Business logic
- **Integrations** — External API wrappers
- **Models** — Database schema

### 4. n8n as Orchestrator
Complex multi-step workflows are defined in n8n JSON and call back into the FastAPI service layer via HTTP. This allows non-engineers to modify workflows via the n8n UI.
