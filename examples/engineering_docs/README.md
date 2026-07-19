# Engineering Docs Automation Example

Automatically summarise, tag, and route engineering documents from Google Drive using Claude AI.

## Use Case
When a new design doc, RFC, or post-mortem is uploaded to Google Drive, Claude reads and summarises it, extracts action items, and posts a summary to the right Slack channel.

## Flow
```
Google Drive Trigger → Claude Summarise → Claude Extract Action Items →
    ├─ RFC         → Post to #engineering-rfcs
    ├─ Post-mortem → Post to #incidents + Airtable log
    └─ Design Doc  → Post to #design-reviews
```

## API Calls
```bash
# List recent Drive files
curl http://localhost:8000/api/v1/google/drive/files?max_results=5

# Summarise a document
curl -X POST http://localhost:8000/api/v1/ai/summarize \
  -H "Content-Type: application/json" \
  -d @example_payload.json

# Extract action items
curl -X POST http://localhost:8000/api/v1/ai/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "...",
    "fields": ["owner", "deadline", "action_items", "stakeholders", "priority"]
  }'
```
