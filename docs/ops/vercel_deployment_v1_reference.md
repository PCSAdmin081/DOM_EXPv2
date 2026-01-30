# Vercel Deployment Guide (V1 Reference)

> **REFERENCE ONLY** — V2 deployment differs (Vercel control plane + self-hosted runner). If this includes routing assumptions that are now wrong, see "V2 Differences" section below.

This application is configured to deploy to Vercel as a serverless function.

## V2 Differences

- V2 uses Vercel for control plane only (no long-running jobs)
- Runner service is self-hosted (separate from Vercel)
- All heavy work is delegated to runner via HTTP
- No scheduling in Vercel — use external cron or Vercel Cron Jobs

## Architecture

- **Entrypoint**: `api/index.py` - imports the FastAPI app from `domain_expansion.app.main`
- **Routing**: `vercel.json` routes all requests to the Python function
- **Scheduler**: Automatically disabled on Vercel (serverless doesn't support background jobs)

## Environment Variables

### Quick Setup (Recommended)

If environment variables are missing or corrupted, use the repair tool:

```bash
python3 scripts/repair_env.py
```

This will:
- Reconstruct missing variables from existing sources
- Generate secure defaults (SECRET_KEY, BOOTSTRAP_TOKEN)
- Create `config/env.local` for import into Vercel
- Generate `artifacts/env_repair_report.json` (metadata only, no secrets)

Then:
1. Review `config/env.local`
2. Import variables into Vercel Dashboard → Settings → Environment Variables
3. Redeploy
4. Verify with `GET /api/v1/ops/debug/env`

### Manual Setup

Set these in Vercel Dashboard → Settings → Environment Variables:

### Required

- `SECRET_KEY` - Random secret key (min 32 characters) for session encryption
- `ADMIN_USERNAME` - Admin user login username (will be created/updated on startup)
- `ADMIN_PASSWORD` - Admin user login password (plaintext, will be hashed automatically)
  - **Alternative**: `ADMIN_PASSWORD_HASH` - Pre-hashed password (if you prefer supplying hash)
- `ADMIN_EMAIL` - Admin user email
- `AUTH_DEBUG_TOKEN` - Random token for auth debug endpoint (optional but recommended for troubleshooting)
- `BOOTSTRAP_TOKEN` - Random token for admin bootstrap endpoint (required for password recovery)

### Database

- `DATABASE_URL` - **Database connection string (REQUIRED)**
  - **Recommended**: PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/dbname`)
  - **Not recommended**: SQLite on Vercel (files are ephemeral and will be lost between deployments)
  - Use a managed database service like:
    - Supabase (free tier available)
    - PlanetScale (MySQL)
    - Railway (PostgreSQL)
    - Neon (PostgreSQL)

#### Supabase Postgres

When using Supabase, paste the connection string directly into `DATABASE_URL`:

1. **Get Connection String**: In Supabase Dashboard → Project Settings → Database → Connection String → URI
2. **Paste as-is**: The app will automatically normalize `postgresql://` to `postgresql+psycopg://`
3. **URL Encoding**: If your password contains special characters, URL-encode them:
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `%` becomes `%25`
   - etc.
4. **SSL Mode**: Supabase requires SSL. Add `?sslmode=require` to the connection string if not already present:
   - Example: `postgresql://user:pass@host:5432/dbname?sslmode=require`
5. **Automatic Normalization**: The app automatically converts:
   - `postgresql://` → `postgresql+psycopg://`
   - `postgres://` → `postgresql+psycopg://`
   - `postgresql+psycopg2://` → `postgresql+psycopg://`

6. **Schema Guard**: On startup, the app automatically ensures required columns exist:
   - `users.hashed_password` (TEXT)
   - `users.role` (VARCHAR(20))
   - `users.active` (BOOLEAN)
   - This prevents "column does not exist" errors on older databases

7. **Admin Bootstrap Endpoint**: If you need to reset the admin password:
   - `POST /api/v1/admin/bootstrap` with header `X-Bootstrap-Token: <BOOTSTRAP_TOKEN>`
   - Uses `ADMIN_USERNAME` and `ADMIN_PASSWORD` from env vars
   - Creates or updates the admin user automatically

### Optional (for Notion integration)

- `NOTION_TOKEN` - Notion API integration token
- `NOTION_ACCOUNTS_DB_ID` - Notion database ID for accounts/pages database (required for Pages sync)
- `CAPTION_BUILDER_ENABLED` - Set to `true` to enable Caption Builder
- `CAPTION_BUILDER_DB_ID` - Notion database ID for Caption Builder
- `CAPTION_BUILDER_CITY_PROP` - Property name for City (default: "City")
- `CAPTION_BUILDER_NICHE_PROP` - Property name for Niche (default: "Niche")
- `CAPTION_BUILDER_HOOK_PROP` - Property name for Hook Family (default: "Hook Family")
- `CAPTION_BUILDER_CTA_PROP` - Property name for Micro-CTA (default: "Micro-CTA")
- `CAPTION_BUILDER_CREATOR_HANDLE_PROP` - Property name for Creator Handle (default: "Creator Handle")
- `CAPTION_BUILDER_FINAL_CAPTION_PROP` - Property name for Final Caption (default: "Final Caption")

### Optional (for Runner / Clawdbot integration)

- `RUNNER_ENABLED` - Set to `true` to enable the external runner integration
- `RUNNER_BASE_URL` - HTTPS URL of the runner service (via Cloudflare Tunnel / reverse proxy)
- `RUNNER_TOKEN` - Shared secret used as `X-Runner-Token` between control plane and runner

### Optional (for Meta integration - scheduler disabled on Vercel)

- `META_ACCESS_TOKEN` - Meta Graph API access token
- `META_APP_ID` - Meta App ID
- `META_APP_SECRET` - Meta App Secret
- `META_SYNC_ENABLED` - Set to `true` to enable Meta sync (note: scheduler disabled on Vercel)
- `META_SYNC_INTERVAL_MINUTES` - Interval for Meta sync (default: 60)

### Optional (for Metrics)

- `METRICS_COLLECTION_ENABLED` - Set to `true` to enable metrics collection (note: scheduler disabled on Vercel)
- `METRICS_COLLECTION_INTERVAL_MINUTES` - Interval for metrics collection (default: 15)

### Storage Paths (optional, defaults provided)

- `STORAGE_PATH` - Base storage path (default: `./data`)
- `UPLOADS_PATH` - Uploads directory (default: `./data/uploads`)
- `OUTPUTS_PATH` - Outputs directory (default: `./data/outputs`)
- `CACHE_PATH` - Cache directory (default: `./data/cache`)
- `LOGS_PATH` - Logs directory (default: `./data/logs`)

## Deployment

1. **Connect Repository**: Link your GitHub repository to Vercel
2. **Set Environment Variables**: Add all required environment variables in Vercel Dashboard
3. **Deploy**: Vercel will automatically detect `vercel.json` and deploy

## Important Notes

### Scheduler Disabled on Vercel

The background job scheduler is automatically disabled when `VERCEL=1` is detected (set automatically by Vercel). This means:
- Metrics collection jobs won't run
- Meta sync jobs won't run
- Nearsight scrape jobs won't run
- Boot-time jobs are skipped

To run scheduled jobs, use:
- External cron service (e.g., cron-job.org) calling your API endpoints
- Vercel Cron Jobs (if available in your plan)
- Separate worker service

### Database Persistence

SQLite databases in the default `./data` directory are **ephemeral** on Vercel. They will be lost on:
- Deployment
- Function cold start
- Container restart

**Solutions**:
1. Use an external database (PostgreSQL, MySQL, etc.) via `DATABASE_URL`
2. Use Vercel's persistent storage (if available)
3. Store database in `/tmp` (still ephemeral but survives warm starts)
4. Use a database service like Supabase, PlanetScale, or Railway

### Static Files

Static file mounting is disabled on Vercel. If you need static file serving:
- Use Vercel's static file hosting
- Use a CDN (Cloudflare, etc.)
- Store files in an external service (S3, etc.)

## Deployment Checklist

### Before First Deployment

1. **Set Required Environment Variables** in Vercel Dashboard → Settings → Environment Variables:
   - [ ] `SECRET_KEY` - Random secret key (min 32 characters)
   - [ ] `ADMIN_USERNAME` - Admin user login username
   - [ ] `ADMIN_PASSWORD` - Admin user login password
   - [ ] `ADMIN_EMAIL` - Admin user email
   - [ ] `DATABASE_URL` - Database connection string (PostgreSQL recommended)

2. **Set Optional Environment Variables** (if using features):
   - [ ] `NOTION_TOKEN` - For Notion integration
   - [ ] `CAPTION_BUILDER_ENABLED` - Set to `true` to enable
   - [ ] `CAPTION_BUILDER_DB_ID` - Notion database ID
   - [ ] `META_ACCESS_TOKEN` - For Meta/Instagram integration

3. **After Setting Environment Variables**:
   - [ ] **Redeploy** the application (Vercel → Deployments → Redeploy)
   - Environment variables are only available after redeployment

### After Deployment

Verify the following:

- [ ] `/healthz` returns `{"status": "healthy", "configured": true}` (or `{"status": "unhealthy", "configured": false}` if setup needed)
- [ ] `/setup` loads and shows configuration status
- [ ] `/` redirects to `/login` or `/dashboard` (not 404 or 500)
- [ ] `/login` loads the login page
- [ ] `/dashboard` loads after authentication
- [ ] `/captorator` loads the Captorator UI
- [ ] `/api/v1/captorator/builder/schema` returns 200 or clear config error
- [ ] Server logs show "scheduler disabled (Vercel environment)" on startup
- [ ] All routes respond correctly (no 404s for expected endpoints)

### Syncing Notion Pages to Dashboard

To populate the dashboard with pages from your Notion "accounts/pages" database:

1. **Set Required Environment Variables**:
   - `NOTION_TOKEN` - Your Notion API integration token
   - `NOTION_ACCOUNTS_DB_ID` - The database ID of your Notion accounts/pages database
   - `BOOTSTRAP_TOKEN` - A secure random token for protecting the sync endpoint

2. **Call the Sync Endpoint**:
   ```bash
   curl -X POST https://your-app.vercel.app/api/v1/notion/sync/accounts \
     -H "X-Bootstrap-Token: YOUR_BOOTSTRAP_TOKEN"
   ```

   The endpoint will:
   - Fetch all rows from the Notion accounts/pages database
   - Map them to `social_pages` table (with property name fallbacks)
   - Upsert based on `(platform, handle)` combination
   - Return a summary: `{"success": true, "fetched": N, "inserted": X, "updated": Y, "skipped": Z, "errors": 0}`

3. **Property Mapping**:
   The sync endpoint tries multiple property names for flexibility:
   - **Platform**: "Platform" or "platform"
   - **Name**: "Name", "Page", or "Title"
   - **Handle**: "Handle", "Username", or "Creator Handle" (required)
   - **Page ID**: "Page ID", "PageId", "IG ID", or "FB ID"
   - **Active**: "Active" or "Enabled" (defaults to `true` if missing)

4. **Note**: Vercel environment variables must be set separately from your local `.env` file. After setting them in Vercel Dashboard, redeploy for changes to take effect.

### Troubleshooting

If `/healthz` returns `{"status": "unhealthy", "configured": false}`:
1. Visit `/setup` to see which environment variables are missing
2. Add missing variables in Vercel Dashboard
3. Redeploy the application
4. Check `/healthz` again

## Troubleshooting

### Template Not Found

If you see "Template not found" errors:
- Check that `domain_expansion/app/templates/` exists in your repository
- Verify template paths are correct (see `pages.py` and `frontend.py`)

### Import Errors

If you see import errors:
- Verify `requirements.txt` is at the repo root
- Check that all dependencies are listed in `requirements.txt`
- Ensure `PYTHONPATH` is set correctly (handled by `vercel.json`)

### Database Errors

If you see database errors:
- Verify `DATABASE_URL` is set correctly
- Check that the database file path is writable
- Consider using an external database for persistence

### Scheduler Still Running

If scheduler appears to be running:
- Check logs for "scheduler disabled (Vercel environment)"
- Verify `VERCEL=1` is set (Vercel sets this automatically)
- Check that `DISABLE_SCHEDULER=1` is not conflicting
