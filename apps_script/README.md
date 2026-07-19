# Google Apps Script — Enterprise AI Integration

This folder contains Google Apps Script (`.gs`) files that add AI-powered automation directly inside Google Sheets, with a custom sidebar menu that calls the FastAPI backend.

## 📁 Files

| File | Purpose |
|---|---|
| `appsscript.json` | OAuth scopes manifest |
| `Config.gs` | Shared `apiPost()` / `apiGet()` helpers, toast, logging |
| `WorkflowAutomation.gs` | Custom menu, health check, workflow trigger, execution logs |
| `EmailProcessor.gs` | Gmail → Sheet triage, classify rows, summarise cells |
| `SheetTriggers.gs` | `onEdit`, `onFormSubmit`, Calendar sync, AI-fill dialog |
| `InvoiceProcessor.gs` | AI invoice field extraction, Airtable sync, summary report |

---

## 🚀 Quick Setup

### Step 1 — Open Apps Script Editor
In any Google Sheet:  
`Extensions → Apps Script`

### Step 2 — Copy the files
Paste each `.gs` file into a new Script file in the editor.  
Also paste `appsscript.json` into **Project Settings → Edit appsscript.json**.

### Step 3 — Configure the API URL
Go to **Project Settings → Script Properties** and add:

| Key | Value |
|---|---|
| `API_BASE_URL` | `https://your-domain.com/api/v1` |
| `AIRTABLE_BASE_ID` | `appXXXXXXXX` *(optional)* |

> 💡 For local dev, use [ngrok](https://ngrok.com) to expose your local server:  
> `ngrok http 8000` → copy the HTTPS URL → set as `API_BASE_URL`

### Step 4 — Install triggers
Run `installTriggers()` once from the Apps Script editor (`Run → installTriggers`).

### Step 5 — Reload your spreadsheet
The **⚡ AI Workflows** menu appears in the toolbar.

---

## ✨ Menu Features

| Menu Item | What it does |
|---|---|
| 🤖 Classify selected rows | AI-classifies the text in selected cells |
| 📄 Summarise selected cell | AI-summarises a long text cell |
| 📧 Process inbox emails | Reads Gmail, classifies with AI, logs to sheet |
| 📅 Sync calendar events | Pulls next 20 events into a Calendar sheet |
| ✨ AI-fill sheet with data | Claude generates structured data into the active sheet |
| 🔄 Trigger workflow via API | Pick and run any workflow from the API |
| 💚 Check API health | Shows all integration statuses |
| 📋 View execution logs | Dumps execution history into a sheet |

---

## 🔗 API Endpoints Used

| Script | Endpoints Called |
|---|---|
| `WorkflowAutomation.gs` | `GET /health`, `GET /workflows`, `POST /workflows/{id}/execute`, `GET /executions` |
| `EmailProcessor.gs` | `GET /google/gmail/messages`, `POST /ai/classify`, `POST /ai/summarize` |
| `SheetTriggers.gs` | `POST /ai/classify`, `POST /ai/extract`, `GET /google/calendar/events`, `POST /google/sheets/{id}/ai-fill` |
| `InvoiceProcessor.gs` | `POST /ai/extract`, `POST /ai/summarize`, `POST /airtable/bases/{id}/tables/Invoices/records` |

---

## 📊 Auto-created Sheets

| Sheet Name | Created By | Contents |
|---|---|---|
| `Email Triage` | `processInboxEmails()` | Classified Gmail messages |
| `CRM` | `onFormSubmit()` | AI-enriched form submissions |
| `Calendar` | `syncCalendarEvents()` | Upcoming calendar events |
| `Execution Logs` | `viewExecutionLogs()` | Workflow execution history |
| `Invoices` | `processAllInvoices()` | Extracted invoice fields |
| `Invoice Summary` | `generateInvoiceSummary()` | AI-written invoice summary |
| `_AI_Logs` | `logToSheet()` | Internal action log |

---

## 🔑 Required OAuth Scopes (in `appsscript.json`)
- `spreadsheets` — Read/write Google Sheets
- `gmail.readonly` + `gmail.send` — Read inbox, send emails
- `calendar` — Read/write calendar events
- `drive.readonly` — List files
- `script.external_request` — Call external FastAPI URL

---

## 🌐 Connecting to n8n
You can also trigger n8n webhooks from Apps Script:

```javascript
function triggerN8nWebhook() {
  const resp = apiPost('/n8n/trigger', {
    webhook_path: 'email-triage',
    payload: { source: 'apps_script', timestamp: new Date().toISOString() }
  });
  Logger.log(resp);
}
```
