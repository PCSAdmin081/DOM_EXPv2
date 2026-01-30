# Setup Guide (V1 Reference)

> **REFERENCE ONLY** — Update steps will be replaced by V2 instructions.


## Initial Setup

### 1. Install Dependencies

```bash
cd domain_expansion
pip install -r requirements.txt
```

### 2. Create Environment File

Create a `.env` file in the `domain_expansion` directory with the following variables:

```bash
# Database
DATABASE_URL=sqlite:///./data/domain_expansion.db

# Storage paths
STORAGE_PATH=./data
UPLOADS_PATH=./data/uploads
OUTPUTS_PATH=./data/outputs
CACHE_PATH=./data/cache
LOGS_PATH=./data/logs

# Server
HOST=127.0.0.1
PORT=8000
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE_MIN_32_CHARS
SESSION_COOKIE_NAME=domain_expansion_session
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SECURE=false

# Admin bootstrap
ADMIN_USERNAME=admin
ADMIN_PASSWORD=CHANGE_THIS_PASSWORD
ADMIN_EMAIL=admin@example.com

# Job scheduler
SCHEDULER_ENABLED=true
METRICS_COLLECTION_SCHEDULE=0 30 23 * * *
NEARSIGHT_SCHEDULE=0 0 * * * *

# Optional: External access URL
BASE_URL=http://localhost:8000
```

**IMPORTANT**: 
- Generate a secure `SECRET_KEY` (at least 32 characters)
- Change `ADMIN_PASSWORD` to a strong password
- The admin user will be created automatically on first run

### 3. Run Smoke Test

```bash
python smoke_test.py
```

This will verify:
- Database initialization
- Module imports
- Basic functionality

### 4. Start the Application

```bash
python run.py
```

The application will be available at `http://localhost:8000`

## First Login

1. Navigate to `http://localhost:8000`
2. Login with the admin credentials from your `.env` file
3. You'll be redirected to the dashboard

## Adding Social Pages

To track metrics for social pages, you can:

1. **Via API** (requires authentication):
```bash
curl -X POST http://localhost:8000/api/v1/dashboard/pages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "name": "Example Page",
    "handle": "@example"
  }'
```

2. **Via Database** (direct SQL):
```sql
INSERT INTO social_pages (platform, name, handle, active) 
VALUES ('instagram', 'Example Page', '@example', 1);
```

3. **Via Python script**:
```python
from app.db import SessionLocal
from app.models import SocialPage

db = SessionLocal()
page = SocialPage(
    platform="instagram",
    name="Example Page",
    handle="@example",
    active=True
)
db.add(page)
db.commit()
```

## Adding Metrics

Metrics can be added manually or via the metrics collection job:

```python
from app.db import SessionLocal
from app.models import MetricsSnapshot
from datetime import datetime

db = SessionLocal()
snapshot = MetricsSnapshot(
    page_id=1,
    timestamp=datetime.utcnow(),
    followers=10000,
    source="manual"
)
db.add(snapshot)
db.commit()
```

## VPS Deployment (Primary)

**DOMAIN_EXPANSION is designed for dedicated VPS hosting.** See [DEPLOYMENT.md](DEPLOYMENT.md) for complete VPS deployment instructions including:
- Ubuntu LTS setup
- Cloudflare Tunnel configuration
- Cloudflare Access setup
- Systemd service configuration
- Backup strategy
- Git-based deployment workflow

## Local Development / Testing

1. Install Python 3.11+
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env`
4. Run with systemd or screen/tmux:

**systemd service** (`/etc/systemd/system/domain-expansion.service`):
```ini
[Unit]
Description=DOMAIN_EXPANSION Dashboard
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/domain_expansion
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/domain_expansion/run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable domain-expansion
sudo systemctl start domain-expansion
```

## Access Configuration

### VPS Deployment

For production VPS deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Cloudflare Tunnel setup for `dashboard.pthwyconnect.com`
- Cloudflare Access configuration for staff-only access
- Systemd service setup
- Backup automation

### Local Development

For local testing, the app binds to `127.0.0.1:8000` by default. Access at `http://localhost:8000`.

## Troubleshooting

### Database locked errors
- Ensure only one instance is running
- Check file permissions on `data/` directory

### Module import errors
- Verify `Captorator_v1_2` and `nearsightv1_2_3` directories exist in parent directory
- Check Python path includes project root

### Authentication issues
- Verify `SECRET_KEY` is set and at least 32 characters
- Clear browser cookies and try again

### Scheduler not running
- Check `SCHEDULER_ENABLED=true` in `.env`
- Verify cron expressions are valid (6 parts: second minute hour day month day_of_week)

## Next Steps

- Add social pages to track
- Configure metrics collection job
- Set up Nearsight feed sources
- Customize dashboard views
- Add additional users with appropriate roles
