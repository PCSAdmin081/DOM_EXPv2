# DOMAIN_EXPANSION

**VPS-Based Internal Operations Platform** for Pathway Connection Solutions / Overly Marketing Group.

Accessible via `dashboard.pthwyconnect.com` through Cloudflare Tunnel with staff-only authentication.

> See `../DOMAIN_EXPANSION_VPS_Master_Briefing.md` for the complete strategy and architecture overview.

## ⚠️ CRITICAL: Environment File Protection

**NEVER edit `.env` or `.env.save` via automated patches or AI agents.**

These files contain sensitive credentials (Notion tokens, Meta API keys, database IDs) that are:
- **Not recoverable** if overwritten (they're gitignored)
- **Required** for the application to function
- **Unique** to each environment

**If you need to modify configuration:**
1. Manually edit `.env` in your editor
2. Or update `.env.example` (template only, no secrets) and document changes
3. Never use automated tools to "merge" or "update" `.env` files

**Recovery:** If values are lost, check:
- VSCode/Cursor Local History (Timeline view)
- Terminal history (`history | grep NOTION`)
- Time Machine backups
- Deployed server environments
- See `RECOVERED_ENV_VALUES.txt` for recovery template

## Features

- **Dashboard**: Live and historical metrics with graphs for social pages
- **Captorator**: Caption and hashtag generator tool
- **Nearsight**: News headline scraper and selector
- **Authentication**: Role-based access control (admin, ops, viewer)
- **Background Jobs**: Automated metrics collection and scraping
- **Admin/Ops Pages**: System status, job management, user administration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

**Option A: Use Repair Tool (Recommended)**

If environment variables are missing or corrupted:

```bash
python3 scripts/repair_env.py
```

This will generate `config/env.local` with reconstructed values. Review and import into Vercel.

**Option B: Manual Setup**

Copy `config/env.example` to `.env` in the repo root and update the values:

```bash
cp config/env.example .env
# Edit .env with your settings
```

**Note**: The env template is located at `config/env.example` (committed) to avoid tooling conflicts.

**Important**: Change `SECRET_KEY` and `ADMIN_PASSWORD` before first run!

### 3. Run the Application

**Recommended method (safely loads .env, no shell parsing issues):**
```bash
./scripts/run_dev.sh
```

**Alternative method:**
```bash
python run.py
```

**Important**: Do NOT use `set -a && source .env && set +a` - it fails when `.env` values contain spaces or parentheses. Always use `./scripts/run_dev.sh` for development.

The application will be available at `http://localhost:8000`

Default admin credentials (change in `.env`):
- Username: `admin`
- Password: (set in `ADMIN_PASSWORD`)

## Project Structure

```
domain_expansion/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── settings.py           # Configuration
│   ├── db.py                # Database setup
│   ├── models.py             # SQLAlchemy models
│   ├── auth.py               # Authentication utilities
│   ├── init_db.py            # Database initialization
│   ├── scheduler.py           # Background job scheduler
│   ├── routers/              # API routes
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── captorator.py
│   │   ├── nearsight.py
│   │   ├── admin.py
│   │   ├── ops.py
│   │   └── frontend.py
│   ├── modules/               # Module integrations
│   │   ├── captorator_service.py
│   │   └── nearsight_service.py
│   └── templates/             # HTML templates
├── data/                      # Data directory (created automatically)
│   ├── domain_expansion.db   # SQLite database
│   ├── uploads/              # Captorator uploads
│   ├── outputs/               # Generated outputs
│   ├── cache/                 # Cache files
│   └── logs/                  # Log files
├── requirements.txt
├── run.py
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Dashboard
- `GET /api/v1/dashboard/overview` - Network overview
- `GET /api/v1/dashboard/pages/{page_id}` - Page details
- `GET /api/v1/dashboard/pages/{page_id}/timeseries` - Time series data

### Captorator
- `GET /api/v1/captorator` - UI
- `GET /api/v1/captorator/meta` - Metadata
- `POST /api/v1/captorator/generate` - Generate caption
- `POST /api/v1/captorator/upload` - Upload file

### Nearsight
- `POST /api/v1/nearsight/run` - Run scraper
- `GET /api/v1/nearsight/articles` - Get articles
- `GET /api/v1/nearsight/runs` - Get run history

### Admin
- `GET /api/v1/admin/users` - List users
- `POST /api/v1/admin/users` - Create user

### Ops
- `GET /api/v1/ops/status` - System status
- `GET /api/v1/ops/jobs` - List jobs
- `POST /api/v1/ops/jobs/{job_id}/run` - Run job manually
- `GET /api/v1/ops/runner/health` - Runner (Clawdbot) health proxy
- `POST /api/v1/ops/jobs/claw/schema_drift` - Queue Clawdbot schema drift job
- `POST /api/v1/ops/jobs/claw/index_intel` - Queue Clawdbot index intelligence job
- `POST /api/v1/ops/jobs/claw/query_audit` - Queue Clawdbot query audit job
- `GET /api/v1/ops/jobs/recent` - Recent ops jobs from `ops_jobs`
- `GET /api/v1/ops/jobs/{job_id}` - Full ops job record by ID

## Roles

- **viewer**: Can view dashboard and metrics
- **ops**: Can use tools (Captorator, Nearsight) and view ops pages
- **admin**: Full access including user management

## Background Jobs

Jobs are scheduled using APScheduler:

- **metrics_collection**: Collects metrics for all active social pages (default: daily at 23:30)
- **nearsight_scrape**: Runs Nearsight scraper (default: hourly)

Jobs can be managed via the Ops page or API.

## Database

The application uses SQLite by default (configured via `DATABASE_URL`). The database is automatically initialized on first run.

To migrate to PostgreSQL, change `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## Deployment

### VPS Deployment (Primary Strategy)

DOMAIN_EXPANSION is designed for **dedicated VPS hosting** (Ubuntu LTS) with:
- Always-on, stable environment
- Cloudflare Tunnel for secure access
- Cloudflare Access for staff-only authentication
- Subdomain: `dashboard.pthwyconnect.com`
- No direct inbound ports exposed

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete VPS deployment instructions.

### Local Development

For local development and testing:

1. Install Python 3.11+
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env`
4. Run: `python run.py`

The application will be available at `http://localhost:8000`

## Adding Metrics

To add metrics for a social page:

1. Use the API or database to create a `SocialPage` record
2. Create `MetricsSnapshot` records (or use the metrics collection job)
3. Metrics will appear on the dashboard

## Updating Modules

### Captorator

The Captorator module is integrated from `../Captorator_v1_2/`. To update:
1. Update the original Captorator code
2. The integration will automatically use the new version

### Nearsight

The Nearsight module is a Python port. Configuration files are read from `../nearsightv1_2_3/src/config/`.

## Troubleshooting

### Database errors
- Ensure the `data/` directory is writable
- Check `DATABASE_URL` in `.env`

### Module import errors
- Ensure original Captorator and Nearsight directories exist
- Check file paths in `modules/` services

### Authentication issues
- Verify `SECRET_KEY` is set and at least 32 characters
- Check session cookie settings

## Development

**Use the canonical dev runner** (safely loads .env):
```bash
./scripts/run_dev.sh
```

This script uses python-dotenv to load `.env` safely, avoiding shell parsing issues with spaces or special characters in environment variable values. No need to manually source `.env`.

**Alternative: Run with auto-reload manually:**
```bash
uvicorn domain_expansion.app.main:app --reload --host 127.0.0.1 --port 8000
```

Note: Ensure `.env` is in the repo root directory for the script to find it.

## License

Internal use only - Pathway Connection Solutions / Overly Marketing Group
