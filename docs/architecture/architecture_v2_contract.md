# DOMAIN_EXPANSION Architecture — V2 Contract

## V2 Contract Summary

**Control Plane Responsibilities:**
- FastAPI app hosted on Vercel (serverless functions)
- HTTP API endpoints (`/api/ops/*`, `/api/auth/*`, feature-gated routes)
- Frontend HTML routes (`/`, `/tools/*`)
- Authentication and session management
- Database schema management (via schema_guard)
- Job orchestration (creates `ops_jobs` records, forwards to runner via HTTP)
- Feature flag enforcement (gates tables, routes, and behavior)
- **No long-running jobs in Vercel** — all heavy work delegated to runner
- **No scheduling in Vercel** — use external cron or Vercel Cron Jobs

**Runner Responsibilities:**
- Self-hosted FastAPI service (separate from control plane)
- Execute heavy jobs (Clawdbot commands, Nearsight candidate generation, Captorator QC)
- Direct database access (read/write to Postgres)
- Subprocess execution with timeouts
- Update `ops_jobs` table with status and results

**Token/Auth Gating:**
- Runner requires `X-Runner-Token` header matching `RUNNER_TOKEN` env var
- Runner validates job types against `RUNNER_ALLOWLIST`
- Control plane validates runner token before forwarding jobs

**Postgres-Only Requirement:**
- `DATABASE_URL` must be a PostgreSQL connection string
- No SQLite fallback — app crashes on startup if SQLite detected
- Both control plane and runner connect to same Postgres database

**Where Logs Live:**
- All job execution logged in `ops_jobs` table
- Optional `ops_job_events` table for detailed event logs
- Status transitions: `queued` → `running` → `succeeded`/`failed`

**No Long Jobs in Vercel:**
- Vercel functions have execution time limits
- All heavy work must be delegated to runner
- Control plane endpoints must return quickly (< 5-10 seconds)
- Runner accepts jobs quickly and processes asynchronously

---

**Canonical system reference document.**

This document is the authoritative source of truth for system structure, contracts, taxonomy rules, and interaction patterns. It must be kept in sync with the codebase.

**Last Updated**: 2026-01-29

---

## 1. System Overview

### Control Plane (Vercel-Hosted FastAPI)

- **Location**: `domain_expansion/app/main.py`
- **Deployment**: Vercel serverless functions
- **Entrypoint**: `api/index.py` imports `domain_expansion.app.main:app`
- **Constraints**:
  - No reliable background scheduling (serverless functions are ephemeral)
  - No persistent file storage (use Supabase for all data)
  - No long-running processes
  - Scheduler runs only when `SCHEDULER_ENABLED=true` and function is "warm"

**Responsibilities**:
- HTTP API endpoints (`/api/v1/*`)
- Frontend HTML routes (`/`, `/tools/*`)
- Authentication and session management
- Database schema management (via `schema_guard`)
- Job orchestration (creates `ops_jobs` records, forwards to runner)
- Feature flag enforcement (gates tables, routes, and behavior)

### Runner Service (Self-Hosted FastAPI)

- **Location**: `runner/main.py`
- **Deployment**: Self-hosted (same host as Clawdbot)
- **Exposure**: HTTPS via Cloudflare Tunnel or reverse proxy (NOT directly exposed)
- **Authentication**: `X-Runner-Token` header (shared secret)

**Responsibilities**:
- Execute Clawdbot commands (`claw.schema_drift`, `claw.index_intel`, `claw.query_audit`)
- Generate Nearsight event candidates (`nearsight.event_candidates`)
- Generate Captorator QC reports (`captorator.asset_qc`)
- Direct database access (read-only role preferred)
- Subprocess execution with timeouts

**Security Rules**:
- Only predefined job types in `RUNNER_ALLOWLIST` are allowed
- No arbitrary command execution
- Clawdbot Gateway remains loopback-only (127.0.0.1)

### Execution Flow

1. **Ops Jobs** (Clawdbot):
   - Control plane: `POST /api/v1/ops/jobs/claw/*` → creates `ops_jobs` row → forwards to runner
   - Runner: Executes Clawdbot command → returns structured JSON
   - Control plane: Updates `ops_jobs` status/result

2. **Nearsight Pipeline**:
   - Scheduled: `scheduler.py` → `run_nearsight_pipeline()` → scrapes articles → calls runner for candidates → upserts to DB
   - Manual: `POST /api/v1/nearsight/run_now` → same flow
   - Runner: `POST /jobs/nearsight/event_candidates` → deterministic scoring → returns candidates

3. **Captorator**:
   - Control plane: `POST /api/v1/captorator/generate` → generates caption → stores run
   - Runner: `POST /jobs/captorator/asset_qc` → quality checks (future)

---

## 2. Configuration Contract (Environment Variables)

### Canonical Source

- **Definition**: `domain_expansion/app/config_spec.py` (`CANONICAL_ENV_VARS`)
- **Loading**: `domain_expansion/app/settings.py` (ONLY module allowed to read `os.getenv()`)
- **Template**: `config/env.example` (committed, no secrets)
- **Repair Tool**: `scripts/repair_env.py` (generates `config/env.local`)

### Required Variables

| Variable | Purpose | Validation |
|----------|---------|-----------|
| `DATABASE_URL` | Supabase Postgres connection string | Must start with `postgresql://` or `postgres://` |
| `SECRET_KEY` | Session encryption key | Min 32 characters |
| `ADMIN_USERNAME` | Admin login username | Default: `admin` |
| `ADMIN_PASSWORD` | Admin login password (plaintext) | Required |
| `ADMIN_EMAIL` | Admin email address | Required |

### Feature Flags

| Flag | Default | Gates |
|------|---------|-------|
| `NOTION_ENABLED` | `false` | Notion routers, `notion_*` tables |
| `RUNNER_ENABLED` | `false` | Runner client, ops job endpoints |
| `SCHEDULER_ENABLED` | `true` | Background job scheduler |
| `CAPTORATOR_ENABLED` | `false` | Captorator routes, `captorator_*` tables |
| `NEARSIGHT_ENABLED` | `false` | Nearsight routes, `nearsight_*` tables |
| `JOBS_ENABLED` | `false` | Generic job system, `jobs`, `job_runs` tables |

### Explicit Rules

1. **DATABASE_URL is the only database connection key**:
   - Deprecated: `SQLALCHEMY_DATABASE_URL`, `POSTGRES_URL`, `POSTGRES_PRISMA_URL`
   - Normalization: `postgres://` → `postgresql://` (automatic)

2. **SQLite is never allowed**:
   - Production: Raises `RuntimeError` if SQLite detected
   - Local: Allowed only if `APP_ENV=local` and `DB_REQUIRE_POSTGRES=false` (not recommended)

3. **`os.getenv()` usage is forbidden outside `settings.py`**:
   - All env access must go through `settings.<field>`
   - Enforced by `scripts/audit_config.py`

4. **Feature flags must be declared in `config_spec.py`**:
   - New flags require spec update
   - Flags gate tables (via `FEATURE_TABLES`), routes, and behavior

### Environment Repair Workflow

1. **Detect missing/corrupted vars**:
   ```bash
   python3 scripts/repair_env.py
   ```

2. **Outputs**:
   - `config/env.local` (gitignored, contains secrets)
   - `artifacts/env_repair_report.json` (metadata only)

3. **Verify**:
   - `GET /api/v1/ops/debug/env` (shows missing required vars, dialect, flags)

4. **Import to Vercel**:
   - Copy `config/env.local` values into Vercel Dashboard → Settings → Environment Variables
   - Redeploy

### Common Failure Modes

- **"DATABASE_URL required"**: Missing or empty `DATABASE_URL` → run `repair_env.py`
- **"PostgreSQL is required (got dialect=sqlite)"**: Wrong DB URL or fallback occurred → check `DATABASE_URL` format
- **"Settings not loaded"**: Settings initialization failed → check error in logs, verify required vars
- **"relation X does not exist"**: Table missing → `schema_guard` should create it, check feature flags

---

## 3. Database Contract

### Core Tables (Always Required)

Defined in `domain_expansion/app/constants.py` (`CORE_REQUIRED_TABLES`):

- `users` - User accounts with role-based access
- `sessions` - User session tokens
- `social_pages` - Social media pages being tracked
- `metrics_snapshots` - Time-series metrics (follower counts, etc.)
- `ops_jobs` - Operational job execution log

**Enforcement**: Missing core tables cause fatal startup error in all environments.

### Feature-Gated Tables

Defined in `domain_expansion/app/constants.py` (`FEATURE_TABLES`):

| Table | Feature Flag | Purpose |
|-------|--------------|---------|
| `captorator_runs` | `CAPTORATOR_ENABLED` | Captorator caption generation runs |
| `captorator_qc_reports` | `CAPTORATOR_ENABLED` | Quality control reports |
| `nearsight_runs` | `NEARSIGHT_ENABLED` | Nearsight pipeline execution log |
| `nearsight_articles` | `NEARSIGHT_ENABLED` | Scraped news articles |
| `nearsight_event_candidates` | `NEARSIGHT_ENABLED` | Generated content opportunities |
| `jobs` | `JOBS_ENABLED` | Generic job definitions |
| `job_runs` | `JOBS_ENABLED` | Generic job execution log |

**Enforcement**: Missing feature tables cause fatal error in production, warning in local.

### Canonical Table Names

All table names must match SQLAlchemy `__tablename__` exactly:

- Defined in `domain_expansion/app/constants.py` (`TABLE_*` constants)
- Validated by `domain_expansion/app/db/model_registry.py` (startup check)
- Validated by `domain_expansion/app/startup/contract_guard.py` (table name uniqueness, required tables exist)

**Deprecated**:
- `metrics` → use `metrics_snapshots` (canonical name)

### Schema Guard Behavior

**Location**: `domain_expansion/app/db/schema_guard.py`

**When it runs**:
- Once at startup (FastAPI `lifespan` event)
- Never per-request (would cause latency)

**What it does**:
1. Computes expected tables based on feature flags (`get_expected_tables(settings)`)
2. Creates missing tables (idempotent)
3. Adds missing columns via `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (Postgres-only)
4. Creates indexes (idempotent)

**When it should fail**:
- SQLite detected in production → `RuntimeError`
- Postgres-specific statement fails → logs error, raises

**Rules for adding new tables**:
1. Add SQLAlchemy model in `domain_expansion/app/models.py`
2. Add `__tablename__` constant to `constants.py`
3. Add to `CORE_REQUIRED_TABLES` or `FEATURE_TABLES` (with feature flag)
4. Update `config_spec.py` (`CANONICAL_TABLE_NAMES`) if needed
5. `schema_guard` will create it automatically on next startup

---

## 4. API Surface Map

### Router Prefixes

- `/api/v1` - API v1 routes (defined in `constants.py`: `API_VERSION_PREFIX`)
- `/` - Root/frontend routes

### Authentication

- **Public**: `/api/v1/auth/login`, `/setup`, `/healthz`
- **Viewer**: `require_role("viewer")` - read-only access
- **Ops**: `require_any_role("ops", "admin")` - operational endpoints
- **Admin**: `require_role("admin")` - user management, system config

### API Routes

#### `/api/v1/auth/*`
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - Session termination
- `GET /api/v1/auth/me` - Current user info

#### `/api/v1/ops/*`
- `GET /api/v1/ops/status` - System status (ops/admin)
- `GET /api/v1/ops/runner/health` - Runner health proxy (ops/admin)
- `POST /api/v1/ops/jobs/claw/schema_drift` - Queue schema drift job (ops/admin)
- `POST /api/v1/ops/jobs/claw/index_intel` - Queue index intelligence job (ops/admin)
- `POST /api/v1/ops/jobs/claw/query_audit` - Queue query audit job (ops/admin)
- `GET /api/v1/ops/jobs/recent` - Recent ops jobs (ops/admin)
- `GET /api/v1/ops/jobs/{job_id}` - Get specific job (ops/admin)
- `GET /api/v1/ops/debug/db` - DB connection info (ops/admin, no secrets)
- `GET /api/v1/ops/debug/env` - Environment integrity check (ops/admin, no secrets)
- `GET /api/v1/ops/debug/routes` - Route listing (ops/admin)

#### `/api/v1/nearsight/*` (requires `NEARSIGHT_ENABLED=true`)
- `POST /api/v1/nearsight/events/build_candidates` - Trigger candidate generation (ops/admin)
- `GET /api/v1/nearsight/events/candidates` - List candidates (viewer+)
- `POST /api/v1/nearsight/events/{event_id}/approve` - Approve candidate (ops/admin)
- `POST /api/v1/nearsight/events/{event_id}/reject` - Reject candidate (ops/admin)
- `POST /api/v1/nearsight/run_now` - Manual pipeline trigger (ops/admin)

#### `/api/v1/metrics/*`
- `GET /api/v1/metrics/overview` - Network metrics overview (viewer+)
- `GET /api/v1/metrics/timeseries` - Time-series data (viewer+)
- `POST /api/v1/metrics/import_csv` - Import CSV metrics (ops/admin)
- `POST /api/v1/metrics/collect_live` - Collect live metrics (ops/admin)

#### `/api/v1/captorator/*` (requires `CAPTORATOR_ENABLED=true`)
- `POST /api/v1/captorator/generate` - Generate caption (ops/admin)

#### `/api/v1/admin/*` (requires `admin` role)
- `GET /api/v1/admin/users` - List users
- `POST /api/v1/admin/users` - Create user
- `PUT /api/v1/admin/users/{user_id}` - Update user
- `DELETE /api/v1/admin/users/{user_id}` - Delete user

#### `/api/v1/notion/*` (requires `NOTION_ENABLED=true`)
- `POST /api/v1/notion/sync/accounts` - Sync Notion accounts DB (bootstrap token)

### Frontend Routes

- `GET /` - Dashboard (viewer+)
- `GET /tools/nearsight/events` - Nearsight events UI (viewer+)
- `GET /tools/captorator` - Captorator UI (ops/admin)
- `GET /ops/clawdbot` - Ops dashboard (ops/admin)
- `GET /setup` - Setup page (public, shown when settings fail)

---

## 5. Nearsight Taxonomy and Routing Policy

### Location

- **Policy Definition**: `domain_expansion/app/nearsight/routing_policy.py` (operator-editable)
- **Scoring Logic**: `runner/main.py` (`POST /jobs/nearsight/event_candidates`)
- **Pipeline**: `domain_expansion/app/nearsight/pipeline.py`

### Regions

Defined in `routing_policy.py` (`REGIONS`):

- `STATEWIDE_FL` - Florida-wide content
- `ORLANDO` - Orlando metro area
- `TAMPA_BAY` - Tampa Bay metro area
- `ST_PETE` - St. Petersburg specific
- `SOFLO` - South Florida (Miami-Dade, Broward, Palm Beach)
- `SWFL` - Southwest Florida
- `TALLAHASSEE` - Tallahassee area
- `JAX` - Jacksonville metro area
- `GAINESVILLE` - Gainesville area

**Detection**: Token-based matching against article text (lowercase).

### Pages

Defined in `routing_policy.py` (`PAGE_POLICIES`):

- `omg.florida` - Statewide + all regions, weighted categories
- `orlandocertified` - Orlando region, new openings/events focus
- `soflocertified` - SOFLO region, new openings/events focus
- `stpetecertified` - ST_PETE + TAMPA_BAY regions
- `swflcertified` - SWFL region
- `tallycertified` - TALLAHASSEE region
- `jaxvillecertified` - JAX region
- `gvillecertified` - GAINESVILLE region
- `tampabaycertified` - TAMPA_BAY + ST_PETE regions

**Policy Structure**:
- `regions`: List of region names this page accepts
- `category_weights`: Dict mapping category → weight (0.0-1.0)

### Categories

Defined in `routing_policy.py` (`CATEGORY_KEYWORDS`):

- `florida_man`, `weird`, `crime`, `wildlife`, `public_safety`, `weather`, `traffic`, `events`, `new_opening`, `food_drink`, `local_business`, `community`

**Detection**: Keyword matching against article text (lowercase, token-based).

### Deterministic Scoring

**Location**: `runner/main.py` (`POST /jobs/nearsight/event_candidates`)

**Process**:
1. **Text Normalization**: Lowercase, strip whitespace
2. **Region Detection**: Token matching → region name + confidence (0.0-1.0)
3. **Category Detection**: Keyword matching → category name + confidence + signals
4. **Page Routing**:
   - Check if detected region is in page's `regions` list
   - Apply `category_weights` multiplier
   - Select page with highest weighted score → `primary_target_page`
   - Secondary pages: All pages that accept the region (lower score)
5. **Recency Scoring**: Based on article `published_at` (more recent = higher)
6. **Virality Scoring**: Keyword matching (`VIRALITY_KEYWORDS`)
7. **Final Score**: Weighted combination of region confidence, category confidence, recency, virality
8. **Deduplication**: `dedupe_key` = hash of (title_normalized, region, category)

**Signals** (explainable):
- `region_matches`: List of matched region tokens
- `category_matches`: Dict of category → matched keywords
- `virality_matches`: List of matched virality keywords
- `recency_days`: Days since publication

### Deduplication Rules

- **Key**: `dedupe_key` = deterministic hash of (normalized_title, region, category)
- **Upsert**: `POST /api/v1/nearsight/events/build_candidates` upserts by `dedupe_key`
- **Uniqueness**: One candidate per `dedupe_key` (latest wins)

### Operator-Editable vs Core Logic

**Operator-Editable** (`routing_policy.py`):
- Region token lists
- Page policies (regions, category weights)
- Category keyword lists
- Virality keywords

**Core Logic** (do not edit without architecture review):
- Scoring algorithm (`runner/main.py`)
- Deduplication key generation
- Pipeline orchestration (`nearsight/pipeline.py`)

---

## 6. Job Execution Model

### Ops Jobs (`ops_jobs` table)

**Lifecycle**:
1. `queued` - Created by control plane endpoint
2. `running` - Runner accepted job
3. `ok` - Runner completed successfully
4. `error` - Runner failed or timed out

**Fields**:
- `job_type`: String (e.g., `claw.schema_drift`, `nearsight.event_candidates`)
- `status`: Enum (`queued`, `running`, `ok`, `error`)
- `payload`: JSON (input parameters)
- `result`: JSON (runner output)
- `error`: Text (error message if failed)
- `requested_by`: String (username or `scheduled`)

**Flow**:
1. Control plane: `POST /api/v1/ops/jobs/claw/*` → creates row with `status=queued`
2. Control plane: Forwards to runner via `runner_post()`
3. Runner: Executes job → returns JSON
4. Control plane: Updates row with `status=ok` + `result`
5. If error: Updates row with `status=error` + `error`

### Runner Allowlist

**Location**: `runner/main.py` (`RunnerSettings.runner_allowlist`)

**Default**:
- `claw.schema_drift`
- `claw.index_intel`
- `claw.query_audit`
- `nearsight.event_candidates`
- `captorator.asset_qc`

**Configuration**: `RUNNER_ALLOWLIST` env var (comma-separated)

**Security**: Runner rejects any job type not in allowlist.

### Scheduled vs Manual Runs

**Scheduled**:
- Triggered by `APScheduler` (only if `SCHEDULER_ENABLED=true`)
- Runs on cron schedule (defined in `scheduler.py`)
- `requested_by=None` or `requested_by="scheduled"`
- Example: Nearsight pipeline (every 15 minutes, 07:00-22:00 ET)

**Manual**:
- Triggered by API endpoint (e.g., `POST /api/v1/nearsight/run_now`)
- `requested_by=<username>`
- Example: Manual Nearsight scrape + candidate build

**Concurrency Protection**:
- Nearsight pipeline checks `nearsight_runs` table for `status=running`
- Returns `409 Conflict` if already running

### Scheduler Limitations on Vercel

- **No reliable scheduling**: Serverless functions are ephemeral
- **Warm functions only**: Scheduler runs only if function is "warm" (recently invoked)
- **Recommendation**: Use external cron (e.g., Vercel Cron Jobs, GitHub Actions) to hit `POST /api/v1/nearsight/run_now` periodically

---

## 7. File Organization Rules

### Directory Structure

```
domain_expansion/app/
├── __init__.py
├── main.py              # FastAPI app, router registration, lifespan
├── settings.py          # ONLY module allowed to read os.getenv()
├── db.py                # SQLAlchemy engine, session factory
├── models.py            # SQLAlchemy models (table definitions)
├── constants.py         # Centralized string literals (table names, job types, etc.)
├── config_spec.py       # Canonical env var definitions
├── auth.py              # Authentication helpers
├── scheduler.py         # Background job scheduler (APScheduler)
├── routers/             # API route handlers
│   ├── auth.py
│   ├── ops.py
│   ├── nearsight.py
│   ├── metrics.py
│   ├── captorator.py
│   ├── admin.py
│   └── ...
├── db/
│   ├── schema_guard.py  # Idempotent table/column creation
│   ├── model_registry.py # Model introspection for validation
│   └── ...
├── startup/
│   ├── config_guard.py  # Runtime config validation
│   └── contract_guard.py # Table/router contract validation
├── nearsight/
│   ├── pipeline.py      # End-to-end Nearsight pipeline
│   └── routing_policy.py # Operator-editable routing rules
├── integrations/
│   ├── runner_client.py # Runner HTTP client
│   └── ...
├── services/
│   └── ...
└── templates/           # Jinja2 HTML templates
    └── ...
```

### Rules

1. **New routers**: Add to `domain_expansion/app/routers/`, register in `main.py`
2. **New models**: Add to `domain_expansion/app/models.py`, add `__tablename__` constant to `constants.py`
3. **New services**: Add to `domain_expansion/app/services/` or `domain_expansion/app/modules/`
4. **New templates**: Add to `domain_expansion/app/templates/`, reference in frontend router
5. **New scripts**: Add to `scripts/`, make executable (`chmod +x`)

### Do Not Rules (Based on Past Failures)

1. **No raw SQL table name drift**:
   - Always use `constants.py` table name constants
   - Never hardcode table names in raw SQL strings
   - Validated by `audit_config.py` (scans for `FROM`, `INSERT INTO`, etc.)

2. **No env access outside `settings.py`**:
   - Never use `os.getenv()` or `os.environ[]` outside `settings.py`
   - Always use `settings.<field>`
   - Validated by `audit_config.py`

3. **All feature flags must be declared in `config_spec.py`**:
   - New flags require `CANONICAL_ENV_VARS` entry
   - Flags must gate tables (via `FEATURE_TABLES`), routes, and behavior

4. **No SQLite fallback in production**:
   - `db.py` enforces PostgreSQL if `db_require_postgres=true`
   - Production always requires `DATABASE_URL` with Postgres

5. **No per-request schema_guard execution**:
   - `schema_guard` runs once at startup (lifespan event)
   - Per-request execution causes latency and intermittent 503s

6. **No undefined environment symbols**:
   - Never reference `is_vercel`, `VERCEL`, `DISABLE_SCHEDULER` (deprecated)
   - Use `settings.app_env` and `settings.scheduler_enabled`

---

## 8. Change and Maintenance Process

### When ARCHITECTURE.md Must Be Updated

- New environment variables added
- New database tables added
- New API routes added
- New feature flags added
- Routing policy changes (document operator-editable vs core)
- Execution flow changes (control plane ↔ runner)

### When CHANGELOG.md Must Be Updated

- User-visible feature additions
- Breaking changes (API, schema, env vars)
- Security fixes
- Major refactors

**Location**: `domain_expansion/CHANGELOG.md`

### Required Pre-Deploy Checks

1. **Config Audit**:
   ```bash
   python3 scripts/audit_config.py
   ```
   - Validates env var usage against `config_spec.py`
   - Detects raw SQL table name drift
   - Detects duplicate router paths
   - Exits non-zero on errors

2. **Environment Repair** (when env vars change):
   ```bash
   python3 scripts/repair_env.py
   ```
   - Generates `config/env.local` for Vercel import
   - Verifies all required vars present

3. **DB Verification** (after deploy):
   ```bash
   curl https://your-app.vercel.app/api/v1/ops/debug/db
   ```
   - Confirms dialect is `postgresql`
   - Confirms schema is `public`
   - Confirms `can_select=true`

4. **Env Integrity Check** (after deploy):
   ```bash
   curl https://your-app.vercel.app/api/v1/ops/debug/env
   ```
   - Lists missing required vars
   - Confirms feature flags
   - Confirms `database_url.present=true`

### Validation Script Enhancement

**Future**: Update `scripts/audit_config.py` to:
- Check if `ARCHITECTURE.md` exists
- Validate required section headings are present
- Fail if sections are missing (ensures documentation stays in sync)

---

## Appendix: Quick Reference

### Environment Variables (Required)

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname?sslmode=require
SECRET_KEY=<32+ char random string>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<plaintext password>
ADMIN_EMAIL=admin@example.com
```

### Feature Flags

```bash
SCHEDULER_ENABLED=true
NEARSIGHT_ENABLED=true
CAPTORATOR_ENABLED=false
JOBS_ENABLED=false
NOTION_ENABLED=false
RUNNER_ENABLED=false
```

### Core Tables

- `users`, `sessions`, `social_pages`, `metrics_snapshots`, `ops_jobs`

### API Prefixes

- `/api/v1/*` - API routes
- `/` - Frontend routes

### Debug Endpoints

- `GET /api/v1/ops/debug/db` - Database connection info
- `GET /api/v1/ops/debug/env` - Environment integrity
- `GET /api/v1/ops/debug/routes` - Route listing

---

**End of Architecture Document**
