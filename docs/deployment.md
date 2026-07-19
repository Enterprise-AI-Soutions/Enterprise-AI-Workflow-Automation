# Deployment Guide

## Local Development (Recommended for Getting Started)

```bash
# 1. Clone and set up
git clone https://github.com/Enterprise-AI-Soutions/Enterprise-AI-Workflow-Automation.git
cd Enterprise-AI-Workflow-Automation

# 2. Automated setup
python scripts/setup.py

# 3. Edit .env
notepad .env   # Windows
# nano .env    # Linux/macOS

# 4. Run
uvicorn app.main:app --reload --port 8000

# 5. Seed sample data (optional)
python scripts/seed_data.py
```

## Docker Deployment

```bash
# Build and start all services
docker-compose up --build -d

# Services started:
#   - FastAPI app    → http://localhost:8000
#   - n8n            → http://localhost:5678
#   - PostgreSQL     → localhost:5432
#   - Redis          → localhost:6379

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

## Environment Variables

See [`.env.example`](../.env.example) for a full list. Minimum required to start:

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | No* | Enables real Claude AI |
| `GOOGLE_CLIENT_ID` | No* | Enables Gmail/Calendar/Drive |
| `GOOGLE_CLIENT_SECRET` | No* | Required with CLIENT_ID |
| `AIRTABLE_API_KEY` | No* | Enables Airtable records |
| `N8N_API_KEY` | No* | Enables n8n management |

*App runs in demo mode without these.

## Production Checklist

- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY`
- [ ] Use PostgreSQL: `DATABASE_URL=postgresql+asyncpg://...`
- [ ] Set specific `ALLOWED_ORIGINS`
- [ ] Configure TLS/HTTPS
- [ ] Set up log rotation
- [ ] Configure health check monitoring
