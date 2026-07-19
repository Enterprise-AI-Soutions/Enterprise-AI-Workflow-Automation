# ⚡ Enterprise AI Workflow Automation

> A production-ready AI-powered business workflow automation platform using **FastAPI**, **Claude AI**, **Google Workspace** (Gmail · Calendar · Drive · **Sheets**), **Airtable**, **n8n**, **Google Apps Script**, and **Docker**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Claude AI](https://img.shields.io/badge/Claude-3.5_Sonnet-orange?logo=anthropic)](https://anthropic.com)
[![Google Sheets](https://img.shields.io/badge/Google_Sheets-API_v4-34A853?logo=googlesheets)](https://developers.google.com/sheets)
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
| Row edited in Google Sheets | Claude classifies text | Write category to adjacent column |
| Google Form submitted | Claude extracts + classifies | Enrich CRM sheet record |
| Menu click in Google Sheets | Claude generates tabular data | AI-fill sheet with realistic rows |

**All integrations fall back to demo mode** if API keys aren't configured — the app runs immediately with realistic sample data.

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  External Triggers: Gmail · Calendar · Drive · Sheets · Webhooks · Cron  │
│  Google Apps Script (onEdit · onFormSubmit · time-based · menu clicks)   │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────────────┐
│                    FastAPI Backend (port 8000)                            │
│  /api/v1/health · /workflows · /executions · /ai                          │
│  /google · /google/sheets · /airtable · /n8n                             │
└──────────┬──────────────────────────────────────┬────────────────────────┘
           │                                      │
    ┌──────▼──────┐                    ┌──────────▼───────────────┐
    │  SQLite /   │                    │   Claude AI (Anthropic)   │
    │  PostgreSQL │                    │   chat · classify ·       │
    └─────────────┘                    │   extract · summarize     │
                                       └──────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                        n8n Engine (port 5678)                            │
│   email_triage · invoice_processing · meeting_scheduler                  │
└─────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────────┐
│                    Google Apps Script (apps_script/)                     │
│   Config.gs · WorkflowAutomation.gs · EmailProcessor.gs                  │
│   SheetTriggers.gs · InvoiceProcessor.gs                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
Enterprise-AI-Workflow-Automation/
│
├── app/                              # FastAPI application
│   ├── main.py                       # App entry point
│   ├── config.py                     # Pydantic settings
│   ├── api/
│   │   └── deps.py                   # Dependency injection
│   ├── services/
│   │   ├── ai/
│   │   │   └── claude_service.py     # Anthropic / Claude wrapper
│   │   ├── database/
│   │   │   ├── session.py            # Async SQLAlchemy engine
│   │   │   └── base.py               # ORM base + timestamp mixin
│   │   ├── integrations/
│   │   │   ├── google_workspace.py   # Gmail, Calendar, Drive
│   │   │   ├── google_sheets.py      # Google Sheets API v4 ✨
│   │   │   ├── airtable.py           # Airtable REST API
│   │   │   └── n8n.py                # n8n webhook & API
│   │   └── workflow/
│   │       ├── workflow_service.py   # CRUD + execution logic
│   │       └── execution_service.py  # Execution history
│   ├── models/
│   │   ├── workflow.py               # Workflow ORM model
│   │   ├── execution.py              # WorkflowExecution model
│   │   └── user.py                   # User model
│   ├── routers/
│   │   ├── health.py                 # GET /health
│   │   ├── workflows.py              # Workflow CRUD + execute
│   │   ├── executions.py             # Execution history
│   │   ├── ai.py                     # Claude AI endpoints
│   │   ├── google_workspace.py       # Gmail/Calendar/Drive
│   │   ├── google_sheets.py          # Sheets CRUD + AI-fill ✨
│   │   ├── airtable.py               # Airtable CRUD
│   │   └── n8n.py                    # n8n management
│   ├── templates/
│   │   ├── base.html                 # Base layout
│   │   └── dashboard.html            # Interactive dashboard
│   ├── static/
│   │   ├── css/main.css              # Dark-mode design system
│   │   └── js/main.js                # Dashboard JS
│   └── utils/
│       ├── logger.py                 # Structured logging
│       ├── helpers.py                # Utilities
│       └── exceptions.py             # Custom HTTP exceptions
│
├── apps_script/                      # Google Apps Script ✨
│   ├── appsscript.json               # OAuth scopes manifest
│   ├── Config.gs                     # Shared helpers (apiPost, apiGet, toast)
│   ├── WorkflowAutomation.gs         # ⚡ AI Workflows menu, health check, trigger
│   ├── EmailProcessor.gs             # Gmail → Sheet triage, classify, summarise
│   ├── SheetTriggers.gs              # onEdit, onFormSubmit, Calendar sync, AI-fill
│   ├── InvoiceProcessor.gs           # AI invoice extraction + Airtable sync
│   └── README.md                     # Apps Script setup guide
│
├── config/
│   └── logging_config.py             # Logging configuration
│
├── docs/
│   ├── architecture.md               # System architecture
│   └── deployment.md                 # Deployment guide
│
├── examples/
│   ├── gmail_processing/             # Email triage example
│   ├── invoice_processing/           # Invoice AI extraction
│   ├── crm/                          # CRM lead scoring
│   ├── engineering_docs/             # Doc summarisation
│   └── google_sheets/                # Sheets read/write + AI-fill ✨
│
├── tests/
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_health.py
│   ├── test_workflows.py
│   ├── test_ai.py
│   ├── test_integrations.py
│   └── test_google_sheets.py         # 12 Sheets endpoint tests ✨
│
├── n8n/
│   └── workflows/
│       ├── email_triage.json
│       ├── invoice_processing.json
│       └── meeting_scheduler.json
│
├── alembic/                          # DB migrations
├── docker/
│   ├── Dockerfile                    # Production image
│   └── Dockerfile.dev                # Dev with hot reload
├── scripts/
│   ├── setup.py                      # One-shot setup
│   └── seed_data.py                  # Sample data seeder
│
├── .env.example                      # All env vars documented
├── docker-compose.yml                # Full stack: app+pg+redis+n8n
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
| GET | `/api/v1/health` | App + all integration statuses |
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
| **POST** | **`/api/v1/ai/classify`** | Classify text into categories |
| **POST** | **`/api/v1/ai/extract`** | Extract structured fields |
| **POST** | **`/api/v1/ai/generate-workflow`** | AI-generate workflow steps |
| GET | `/api/v1/google/gmail/messages` | List emails |
| POST | `/api/v1/google/gmail/send` | Send email |
| GET | `/api/v1/google/calendar/events` | List calendar events |
| POST | `/api/v1/google/calendar/events` | Create calendar event |
| GET | `/api/v1/google/drive/files` | List Drive files |
| **GET** | **`/api/v1/google/sheets`** | List spreadsheets from Drive ✨ |
| **POST** | **`/api/v1/google/sheets`** | Create new spreadsheet ✨ |
| **GET** | **`/api/v1/google/sheets/{id}`** | Get spreadsheet metadata ✨ |
| **GET** | **`/api/v1/google/sheets/{id}/values/{range}`** | Read cell values ✨ |
| **PUT** | **`/api/v1/google/sheets/{id}/values/{range}`** | Write cell values ✨ |
| **POST** | **`/api/v1/google/sheets/{id}/append`** | Append rows ✨ |
| **DELETE** | **`/api/v1/google/sheets/{id}/values/{range}`** | Clear range ✨ |
| **POST** | **`/api/v1/google/sheets/{id}/batch-read`** | Read multiple ranges ✨ |
| **POST** | **`/api/v1/google/sheets/{id}/format-headers`** | Style header row ✨ |
| **POST** | **`/api/v1/google/sheets/{id}/ai-fill`** | Claude generates data into sheet ✨ |
| GET | `/api/v1/airtable/bases` | List Airtable bases |
| GET | `/api/v1/airtable/bases/{b}/tables/{t}/records` | List records |
| POST | `/api/v1/airtable/bases/{b}/tables/{t}/records` | Create record |
| GET | `/api/v1/n8n/workflows` | List n8n workflows |
| POST | `/api/v1/n8n/trigger` | Trigger n8n webhook |

---

## 🔌 Integrations

| Integration | Env Variables | Docs |
|---|---|---|
| Claude AI | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| Gmail | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | [Google Cloud Console](https://console.cloud.google.com) |
| Google Calendar | Same as Gmail | — |
| Google Drive | Same as Gmail | — |
| **Google Sheets** | Same as Gmail | [Sheets API](https://developers.google.com/sheets/api) ✨ |
| Airtable | `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID` | [airtable.com/account](https://airtable.com/account) |
| n8n | `N8N_API_KEY`, `N8N_BASE_URL` | [docs.n8n.io](https://docs.n8n.io) |
| **Google Apps Script** | Script Properties (`API_BASE_URL`) | [apps_script/README.md](apps_script/README.md) ✨ |

---

## 📊 Google Sheets Features

### REST API Endpoints
Read, write, append, clear, batch-read, and format spreadsheets directly from the API.

```bash
# AI-generate a spreadsheet full of realistic data
curl -X POST http://localhost:8000/api/v1/google/sheets/YOUR_SHEET_ID/ai-fill \
  -H "Content-Type: application/json" \
  -d '{
    "headers": ["Name", "Email", "Company", "Revenue", "Status"],
    "prompt": "B2B SaaS leads from the US tech sector",
    "rows": 10
  }'
```

### Google Apps Script (in-sheet menu)
Paste the `apps_script/*.gs` files into any Google Sheet for a native **⚡ AI Workflows** menu:

| Menu Action | What It Does |
|---|---|
| 🤖 Classify selected rows | AI-classifies text in selected cells → writes category to next column |
| 📄 Summarise selected cell | Claude summarises a long text cell |
| 📧 Process inbox emails | Reads Gmail, classifies with AI, logs to **Email Triage** sheet |
| 📅 Sync calendar events | Pulls next 20 events into a **Calendar** sheet |
| ✨ AI-fill sheet with data | Claude generates structured rows into the active sheet |
| 🔄 Trigger workflow via API | Pick and run any workflow from the backend |
| 💚 Check API health | Shows all integration statuses in a dialog |
| 📋 View execution logs | Dumps execution history into an **Execution Logs** sheet |

**Setup:** See [apps_script/README.md](apps_script/README.md) for the 3-step installation guide.

---

## 🧪 Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

All **28 tests** pass without any API keys — they use demo mode fallbacks and an in-memory SQLite database.

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
