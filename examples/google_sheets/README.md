# Google Sheets Integration Example

This example shows how to use the `/api/v1/google/sheets/` endpoints to read, write, and AI-generate spreadsheet data.

## Use Cases

| Use Case | Endpoint |
|---|---|
| Log workflow results to a sheet | `POST /google/sheets/{id}/append` |
| Read CRM data from Sheets | `GET /google/sheets/{id}/values/Leads!A:E` |
| AI-generate sample/test data | `POST /google/sheets/{id}/ai-fill` |
| Create a new report spreadsheet | `POST /google/sheets` |
| Batch-read multiple ranges | `POST /google/sheets/{id}/batch-read` |

## Quick Examples

```bash
# List all spreadsheets
curl http://localhost:8000/api/v1/google/sheets

# Create a new spreadsheet
curl -X POST http://localhost:8000/api/v1/google/sheets \
  -H "Content-Type: application/json" \
  -d '{"title": "AI Workflow Results", "sheet_names": ["Executions", "Emails", "Invoices"]}'

# Read values from a range
curl "http://localhost:8000/api/v1/google/sheets/SPREADSHEET_ID/values/Sheet1!A1:E10"

# Write values
curl -X PUT http://localhost:8000/api/v1/google/sheets/SPREADSHEET_ID/values/Sheet1!A1 \
  -H "Content-Type: application/json" \
  -d @write_payload.json

# Append rows
curl -X POST http://localhost:8000/api/v1/google/sheets/SPREADSHEET_ID/append \
  -H "Content-Type: application/json" \
  -d '{"values": [["John Doe", "john@acme.com", "Active", "2025-07-19"]]}'

# AI-generate sheet data (uses Claude AI)
curl -X POST http://localhost:8000/api/v1/google/sheets/SPREADSHEET_ID/ai-fill \
  -H "Content-Type: application/json" \
  -d @ai_fill_payload.json
```
