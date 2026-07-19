# ⚡ Enterprise AI Workflow Automation

> A production-ready AI-powered business workflow automation platform using **FastAPI**, **Claude AI**, **Google Workspace**, **Airtable**, **n8n**, and **Docker**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Claude AI](https://img.shields.io/badge/Claude-3.5_Sonnet-orange?logo=anthropic)](https://anthropic.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 What It Does

This platform lets you build intelligent, AI-driven business workflows that connect your tools automatically:

| Trigger | AI Processing | Action |
|---|---|---|
| New email arrives | Claude classifies intent | Route to CRM, auto-reply |
| Invoice uploaded | Claude extracts fields | Log to Airtable, notify team |
| Meeting requested | Claude parses details | Create Calendar event, send invite |
| New Drive document | Claude summarises | Post to Slack / notify stakeholders |

**All integrations fall back to demo mode** if API keys aren't configured — the app runs immediately with realistic sample data.

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  External Triggers: Gmail · Calendar · Drive · Webhooks · Cron   │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend (port 8000)                     │
│  /api/v1/health · /workflows · /executions · /ai                  │
│          /google · /airtable · /n8n                               │
└──────────┬─────────────────────────────────┬─────────────────────┘
           │                                 │
    ┌──────▼──────┐                 ┌────────▼──────────────┐
    │  SQLite /   │                 │  Claude AI (Anthropic) │
    │  PostgreSQL │                 │  chat · classify ·     │
    └─────────────┘                 │  extract · summarize   │
                                    └───────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│                         n8n Engine (port 5678)                   │
│   email_triage · invoice_processing · meeting_scheduler          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
Enterprise-AI-Workflow-Automation/
│
├── app/                          # FastAPI application
│   ├── main.py                   # App entry point
│   ├── config.py                 # Pydantic settings
│   ├── api/
│   │   └── deps.py               # Dependency injection
│   ├── services/
│   │   ├── ai/
│   │   │   └── claude_service.py # Anthropic / Claude wrapper
│   │   ├── database/
│   │   │   ├── session.py        # Async SQLAlchemy engine
│   │   │   └── base.py           # ORM base + timestamp mixin
│   │   ├── integrations/
│   │   │   ├── google_workspace.py  # Gmail, Calendar, Drive
│   │   │   ├── airtable.py          # Airtable REST API
│   │   │   └── n8n.py               # n8n webhook & API
│   │   └── workflow/
│   │       ├── workflow_service.py   # CRUD + execution logic
│   │       └── execution_service.py # Execution history
│   ├── models/
│   │   ├── workflow.py           # Workflow ORM model
│   │   ├── execution.py          # WorkflowExecution model
│   │   └── user.py               # User model
│   ├── routers/
│   │   ├── health.py             # GET /health
│   │   ├── workflows.py          # Workflow CRUD + execute
│   │   ├── executions.py         # Execution history
│   │   ├── ai.py                 # Claude AI endpoints
│   │   ├── google_workspace.py   # Gmail/Calendar/Drive
│   │   ├── airtable.py           # Airtable CRUD
│   │   └── n8n.py                # n8n management
│   ├── templates/
│   │   ├── base.html             # Base layout
│   │   └── dashboard.html        # Interactive dashboard
│   ├── static/
│   │   ├── css/main.css          # Dark-mode design system
│   │   └── js/main.js            # Dashboard JS
│   └── utils/
│       ├── logger.py             # Structured logging
│       ├── helpers.py            # Utilities
│       └── exceptions.py         # Custom HTTP exceptions
│
├── config/
│   └── logging_config.py         # Logging configuration
│
├── docs/
│   ├── architecture.md           # System architecture
│   └── deployment.md             # Deployment guide
│
├── examples/
│   ├── gmail_processing/         # Email triage example
│   ├── invoice_processing/       # Invoice AI extraction
│   ├── crm/                      # CRM lead scoring
│   └── engineering_docs/         # Doc summarisation
│
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── test_health.py
│   ├── test_workflows.py
│   ├── test_ai.py
│   └── test_integrations.py
│
├── n8n/
│   └── workflows/
│       ├── email_triage.json
│       ├── invoice_processing.json
│       └── meeting_scheduler.json
│
├── alembic/                      # DB migrations
├── docker/
│   ├── Dockerfile                # Production image
│   └── Dockerfile.dev            # Dev with hot reload
├── scripts/
│   ├── setup.py                  # One-shot setup
│   └── seed_data.py              # Sample data seeder
│
├── .env.example                  # All env vars documented
├── docker-compose.yml            # Full stack: app+pg+redis+n8n
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── pytest.ini
└── README.md
```

---

## 🚀 Quick Start

### Option 1 — Local (Recommended)

```bash
# Clone
git clone https://github.com/Enterprise-AI-Soutions/Enterprise-AI-Workflow-Automation.git
cd Enterprise-AI-Workflow-Automation

# Setup (creates venv, installs deps, copies .env)
python scripts/setup.py

# Edit API keys (optional — runs in demo mode without)
# Windows: notepad .env
# Linux:   nano .env

# Activate venv
# Windows: venv\Scripts\activate
# Linux:   source venv/bin/activate

# Run
uvicorn app.main:app --reload

# Seed sample workflows (optional)
python scripts/seed_data.py
```

Open:
- 🖥 Dashboard: http://localhost:8000
- 📖 API Docs: http://localhost:8000/docs
- 💚 Health: http://localhost:8000/api/v1/health

### Option 2 — Docker

```bash
cp .env.example .env  # Edit with your keys

docker-compose up --build -d

# App:  http://localhost:8000
# n8n:  http://localhost:5678 (admin/changeme)
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | App + integration status |
| GET | `/api/v1/workflows` | List all workflows |
| POST | `/api/v1/workflows` | Create workflow |
| GET | `/api/v1/workflows/{id}` | Get workflow |
| PUT | `/api/v1/workflows/{id}` | Update workflow |
| DELETE | `/api/v1/workflows/{id}` | Delete workflow |
| POST | `/api/v1/workflows/{id}/execute` | Run workflow |
| GET | `/api/v1/executions` | Execution history |
| GET | `/api/v1/executions/stats` | Success/failure stats |
| **POST** | **`/api/v1/ai/chat`** | Claude AI chat |
| **POST** | **`/api/v1/ai/summarize`** | Summarise text |
| **POST** | **`/api/v1/ai/classify`** | Classify text |
| **POST** | **`/api/v1/ai/extract`** | Extract fields |
| **POST** | **`/api/v1/ai/generate-workflow`** | AI-generate workflow steps |
| GET | `/api/v1/google/gmail/messages` | List emails |
| POST | `/api/v1/google/gmail/send` | Send email |
| GET | `/api/v1/google/calendar/events` | List events |
| POST | `/api/v1/google/calendar/events` | Create event |
| GET | `/api/v1/google/drive/files` | List files |
| GET | `/api/v1/airtable/bases` | List bases |
| GET | `/api/v1/airtable/bases/{b}/tables/{t}/records` | List records |
| POST | `/api/v1/airtable/bases/{b}/tables/{t}/records` | Create record |
| GET | `/api/v1/n8n/workflows` | List n8n workflows |
| POST | `/api/v1/n8n/trigger` | Trigger webhook |

---

## 🔌 Integrations

| Integration | Env Variables | Docs |
|---|---|---|
| Claude AI | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| Gmail | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | [Google Cloud Console](https://console.cloud.google.com) |
| Google Calendar | Same as Gmail | — |
| Google Drive | Same as Gmail | — |
| Airtable | `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID` | [airtable.com/account](https://airtable.com/account) |
| n8n | `N8N_API_KEY`, `N8N_BASE_URL` | [docs.n8n.io](https://docs.n8n.io) |

---

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

All 16 tests pass without any API keys — they use demo mode fallbacks and an in-memory SQLite database.

---

## 📊 n8n Workflow Examples

Import these from `n8n/workflows/` via the n8n UI (Settings → Import Workflow):

| Workflow | Trigger | AI Step | Actions |
|---|---|---|---|
| `email_triage.json` | Gmail webhook | Claude classify | Airtable + auto-reply |
| `invoice_processing.json` | HTTP webhook | Claude extract | Airtable log + Gmail notify |
| `meeting_scheduler.json` | HTTP webhook | Claude extract | Calendar create + Gmail confirm |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes and add tests
4. Run `pytest` and `ruff check .`
5. Open a Pull Request

---

## 📄 License

MIT — see [LICENSE](LICENSE)
