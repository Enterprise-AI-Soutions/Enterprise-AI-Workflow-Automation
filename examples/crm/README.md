# CRM Automation Example

Sync leads between Gmail, Claude AI, and Airtable for an intelligent CRM pipeline.

## Use Case
When a new lead sends an inquiry email, automatically score the lead using AI, enrich the Airtable CRM record, and assign to the right sales rep.

## Flow
```
Gmail Trigger → Claude Score Lead → Airtable Upsert →
    ├─ Hot Lead  → Assign to Senior AE + Slack alert
    ├─ Warm Lead → Assign to BDR + follow-up sequence
    └─ Cold Lead → Add to nurture campaign
```

## API Calls
```bash
# Score and classify a lead
curl -X POST http://localhost:8000/api/v1/ai/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We are a 500-person company evaluating AI automation vendors with a Q3 budget of $200k",
    "categories": ["Hot Lead", "Warm Lead", "Cold Lead", "Not a Lead"]
  }'

# Create Airtable CRM record
curl -X POST http://localhost:8000/api/v1/airtable/bases/{BASE_ID}/tables/Leads/records \
  -H "Content-Type: application/json" \
  -d @example_payload.json
```
