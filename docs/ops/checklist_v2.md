# V2 Contract Alignment Checklist

This checklist ensures the codebase strictly follows the V2 contract.

## Database Contract

- [x] **DATABASE_URL required and non-sqlite**
  - Settings validation fails fast if DATABASE_URL is missing or empty
  - Settings validation fails fast if DATABASE_URL points to SQLite
  - Session setup raises RuntimeError if not PostgreSQL
  - No SQLite fallback code paths

- [x] **Postgres-only enforcement**
  - `domain_expansion/app/db/session.py` validates PostgreSQL connection
  - `domain_expansion/app/settings.py` validates DATABASE_URL format
  - Both control plane and runner connect to same Postgres database

## Control Plane (Vercel) Contract

- [x] **No long jobs in Vercel**
  - All heavy work delegated to runner via HTTP
  - Control plane endpoints return quickly (< 5-10 seconds)
  - Runner trigger endpoint uses short timeout (10 seconds)

- [x] **Ops jobs always written**
  - All job execution logged in `ops_jobs` table
  - Status transitions: `queued` → `running` → `succeeded`/`failed`
  - Optional `ops_job_events` table for detailed logs

- [x] **Feature flags gate endpoints/UI**
  - Feature flags declared in `config_spec.py`
  - Flags gate tables, routes, and behavior
  - Default: all features disabled

## Runner Contract

- [x] **Runner requires token**
  - Runner validates `X-Runner-Token` header
  - Token must match `RUNNER_TOKEN` env var
  - Invalid token returns 401

- [x] **Runner job allowlist**
  - Runner validates job types against `RUNNER_ALLOWLIST`
  - Unknown job types rejected with 403
  - Default allowlist: nearsight_collect_refresh, captorator_compose, metrics_refresh

- [x] **Runner updates ops_jobs**
  - Runner immediately updates status to `running` on accept
  - Runner updates status to `succeeded` with result JSON on completion
  - Runner updates status to `failed` with error message on failure

## Environment Variables

- [x] **Centralized in settings.py**
  - All env vars defined in `domain_expansion/app/settings.py`
  - No `os.getenv()` usage outside settings.py
  - Required vars: `APP_ENV`, `DATABASE_URL`, `SECRET_KEY`

- [x] **Feature flags declared**
  - All feature flags in `config_spec.py`
  - Flags: `NEARSIGHT_ENABLED`, `CAPTORATOR_ENABLED`, `JOBS_ENABLED`, `NOTION_ENABLED`, `RUNNER_ENABLED`, `FEATURE_METRICS`

## Code Quality

- [x] **No V1 fallback behaviors**
  - No SQLite references in runtime code
  - No metrics_import_ready.csv usage in runtime
  - No "fallback", "default.db", "local.db" in runtime code

- [x] **No hardcoded secrets**
  - No tokens, keys, or passwords in code
  - No hardcoded URLs (use env vars)
  - No secrets in documentation

## Documentation

- [x] **Docs as contracts**
  - Architecture doc in `docs/architecture/architecture_v2_contract.md`
  - V1 docs marked as "REFERENCE ONLY"
  - Root README links to V2 contract and docs index

## Deployment

- [x] **Vercel configuration**
  - `vercel.json` routes all requests to `api/index.py`
  - No long-running processes in Vercel
  - External cron or Vercel Cron Jobs for scheduling

- [x] **Runner deployment**
  - Runner is self-hosted (separate from Vercel)
  - Runner exposed via HTTPS (Cloudflare Tunnel or reverse proxy)
  - Runner connects to same Postgres as control plane

## Database Migrations

### Using Bootstrap Script (Initial Setup)

1. **Run bootstrap script**:
   ```bash
   python scripts/bootstrap_schema.py
   ```

2. **Verify tables created**:
   - Check Postgres: `\dt` should show `ops_jobs` and `ops_job_events`

**Note**: Bootstrap script is for initial setup only. For ongoing migrations, use Alembic.

### Using Alembic (Ongoing Migrations)

1. **Create new migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Review generated migration** in `alembic/versions/`

3. **Apply migration**:
   ```bash
   alembic upgrade head
   ```

4. **Rollback** (if needed):
   ```bash
   alembic downgrade -1
   ```

**Important**: 
- Migrations are NOT run automatically on Vercel
- Run migrations manually after deployment or via CI/CD
- Local development: run `alembic upgrade head` after pulling changes

## Local Validation Steps

### Control Plane Startup Failure Cases

- Missing DATABASE_URL: app should fail immediately at startup with ValidationError
- Invalid DATABASE_URL (SQLite): app should fail immediately with ValueError about PostgreSQL requirement
- Missing OPS_API_KEY in production: app should fail or raise 500 when ops endpoint is accessed

Test commands:
```bash
# Should fail immediately
APP_ENV=prod DATABASE_URL="" uvicorn domain_expansion.main:app

# Should fail immediately
DATABASE_URL="sqlite:///test.db" uvicorn domain_expansion.main:app
```

### Runner Startup Failure Cases

- Missing DATABASE_URL: runner should fail immediately at startup with ValidationError
- Missing RUNNER_TOKEN: runner should fail immediately at startup with ValidationError

Test commands:
```bash
# Should fail immediately
DATABASE_URL="" RUNNER_TOKEN="" uvicorn runner.main:app --port 8010
```

### Happy Path

1. Create job via POST /api/ops/jobs with X-Ops-Key header
2. Trigger runner via POST /api/ops/trigger_runner
3. Verify job transitions: queued → running → succeeded
4. Check ops_jobs table in database for correct status updates

Test commands:
```bash
# Create job
curl -X POST \
  -H "X-Ops-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"job_type": "test_job", "payload": {"test": true}}' \
  http://localhost:8000/api/v1/ops/jobs

# Trigger runner (set RUNNER_URL and RUNNER_TOKEN_OUTBOUND in env)
curl -X POST \
  -H "X-Ops-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"job_type": "nearsight_collect_refresh", "payload": {}}' \
  http://localhost:8000/api/v1/ops/trigger_runner

# Verify in database
# SELECT * FROM ops_jobs ORDER BY created_at DESC LIMIT 5;
```

### Unauthorized Path

- Request to /api/ops/jobs without X-Ops-Key header
- Expected: 401 response with "Invalid or missing X-Ops-Key" message

Test command:
```bash
# Should return 401
curl http://localhost:8000/api/v1/ops/jobs
```

### Secret Leakage Check

- Check all /api/ops/* endpoint responses
- Verify no token values appear in responses
- Verify no runner URL appears in responses
- Use grep to search response bodies for token patterns

Test commands:
```bash
# Check debug endpoint (should not contain secrets)
curl -H "X-Ops-Key: your-key" http://localhost:8000/api/v1/ops/debug/env | grep -i "token\|url\|key"

# Should return empty (no matches)
```

## Testing

- [ ] **Smoke tests** (to be implemented)
  - Control plane boots with valid DATABASE_URL
  - Control plane fails fast with invalid DATABASE_URL
  - Runner accepts jobs with valid token
  - Runner rejects jobs with invalid token

## Notes

- This checklist should be updated as new V2 contract requirements are added
- All items should be verified before production deployment
- See `docs/architecture/architecture_v2_contract.md` for authoritative contract
- Ops endpoints are server-to-server only (no browser access until auth is implemented)
