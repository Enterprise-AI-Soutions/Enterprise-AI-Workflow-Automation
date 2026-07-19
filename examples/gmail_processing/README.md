# Gmail Processing Example

This example demonstrates how to process incoming Gmail messages with Claude AI to auto-classify and route them.

## Use Case
Automatically triage support emails: classify by intent, route urgent tickets, and auto-reply to common queries.

## Flow
```
Gmail Inbox → Webhook → Claude Classify → 
    ├─ Sales Inquiry  → Airtable CRM + Auto-reply
    ├─ Support Request → Create support ticket
    └─ Other          → Tag & archive
```

## Setup

1. Configure your `.env`:
   ```
   ANTHROPIC_API_KEY=your_key
   GOOGLE_CLIENT_ID=your_id
   GOOGLE_CLIENT_SECRET=your_secret
   AIRTABLE_API_KEY=your_key
   AIRTABLE_BASE_ID=your_base_id
   ```

2. Import the n8n workflow:
   ```bash
   # Via n8n UI: Import → upload n8n/workflows/email_triage.json
   ```

3. Send a test request:
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/classify \
     -H "Content-Type: application/json" \
     -d @example_payload.json
   ```

## API Calls Used
- `POST /api/v1/ai/classify`
- `GET /api/v1/google/gmail/messages`
- `POST /api/v1/airtable/bases/{id}/tables/Leads/records`
