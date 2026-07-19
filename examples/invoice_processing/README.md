# Invoice Processing Example

Automate invoice ingestion using Claude AI to extract structured fields and log them to Airtable.

## Use Case
Finance teams receive PDF invoices via email. This workflow extracts key fields automatically, logs them to Airtable, and notifies the finance team.

## Flow
```
Email/Upload → Claude Extract → 
    ├─ invoice_number
    ├─ vendor_name
    ├─ amount
    ├─ due_date
    └─ line_items
→ Airtable Log → Gmail Notify Finance
```

## Setup

```bash
# Test the extraction endpoint directly
curl -X POST http://localhost:8000/api/v1/ai/extract \
  -H "Content-Type: application/json" \
  -d @example_payload.json
```

## Extracted Fields
| Field | Type | Description |
|---|---|---|
| `invoice_number` | string | INV-XXXX |
| `vendor` | string | Company name |
| `amount` | string | Total amount with currency |
| `due_date` | string | ISO date |
| `line_items` | list | Individual line items |
