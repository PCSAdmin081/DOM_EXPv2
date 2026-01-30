# PATCH BATCH 2 INSTRUCTIONS — DOM_EXPv2 Security & Hardening

## Part 1 — Lock down ops endpoints (must-do)

### Step 1: Add OPS_API_KEY to control plane settings

File: domain_expansion/app/settings.py

Add field to Settings class:
- Field name: ops_api_key
- Env var alias: OPS_API_KEY
- Type: str | None
- Default: None

Validation logic:
- In production mode (APP_ENV=prod or APP_ENV=production): OPS_API_KEY must be required
- In development mode: optional but recommended
- Default behavior: required unless explicitly set to dev mode

### Step 2: Create ops API key dependency

File: domain_expansion/app/dependencies.py (create new file)

Create function: require_ops_api_key
- Parameter: x_ops_key header (from X-Ops-Key header)
- Behavior:
  - In production: if OPS_API_KEY not set, raise 500 error
  - In production: if X-Ops-Key missing or mismatch, return 401
  - In development: if OPS_API_KEY is set, validate against it
  - In development: if OPS_API_KEY not set, allow bypass (for local testing)
- Return: the validated key string

### Step 3: Apply dependency to ops router

File: domain_expansion/app/routers/ops.py

Import: from domain_expansion.app.dependencies import require_ops_api_key

Update router definition:
- Add dependencies parameter to APIRouter
- Use Depends(require_ops_api_key) in dependencies list
- This applies to ALL routes in the ops router automatically

### Step 4: Remove client/browser usage

Search for:
- Any frontend code calling /api/ops/* endpoints
- Any UI buttons or forms that trigger ops endpoints
- Any JavaScript/frontend code that includes OPS_API_KEY

Actions if found:
- Remove UI triggers temporarily
- Document that ops endpoints are server-to-server only
- Add note in docs/ops/checklist_v2.md about this restriction
- Future: route through server-only path that injects key (after auth exists)

Acceptance criteria:
- Requests to /api/ops/* without X-Ops-Key header fail with 401
- No UI bundle contains OPS_API_KEY value
- All ops endpoints require X-Ops-Key header

---

## Part 2 — Separate runner token concerns (required)

### Step 5: Rename control plane outbound token variables

File: domain_expansion/app/settings.py

Replace existing fields:
- Old: runner_base_url (alias RUNNER_BASE_URL)
- Old: runner_token (alias RUNNER_TOKEN)

With new fields:
- New: runner_url (alias RUNNER_URL)
- New: runner_token_outbound (alias RUNNER_TOKEN_OUTBOUND)

Rationale:
- RUNNER_URL is clearer than RUNNER_BASE_URL
- RUNNER_TOKEN_OUTBOUND makes explicit this is the token control plane uses when calling runner
- Runner service uses separate RUNNER_TOKEN env var to validate inbound requests

### Step 6: Update runner client

File: domain_expansion/app/integrations/runner_client.py

Update __init__ method:
- Check for settings.runner_url and settings.runner_token_outbound
- Update error message to reference RUNNER_URL and RUNNER_TOKEN_OUTBOUND
- Update self.base_url to use settings.runner_url
- Update self.token to use settings.runner_token_outbound

### Step 7: Update trigger_runner endpoint

File: domain_expansion/app/routers/ops.py

In trigger_runner function:
- Update error check to use settings.runner_url and settings.runner_token_outbound
- Update error message text to reference new variable names

Ensure response contains only:
- job_id (string)
- status (string)
- message (string)

Never include in response:
- runner_url value
- runner_token_outbound value
- Any runner configuration details

### Step 8: Verify runner settings

File: runner/settings.py

Ensure it uses:
- Field: runner_token
- Env var alias: RUNNER_TOKEN
- This is the token runner validates when receiving requests (separate from control plane token)

### Step 9: Update env.example

File: config/env.example

Replace section:
- Old: RUNNER_BASE_URL=http://localhost:8010
- Old: RUNNER_TOKEN=change_me

With new section:
- Heading: Runner integration (control plane side)
- RUNNER_URL=http://localhost:8010
- RUNNER_TOKEN_OUTBOUND=change_me_control_plane_token
- OPS_API_KEY=change_me_ops_key

Add note: Runner service has its own RUNNER_TOKEN in its environment (separate from control plane)

Acceptance criteria:
- /api/ops/trigger_runner response contains only job_id, status, message
- No token or runner URL appears in any API response
- Control plane and runner use separate env var names for clarity

---

## Part 3 — Remove Vercel background-task assumptions (required)

### Step 10: Audit for background work in control plane

Search for these patterns:
- BackgroundTasks import
- background_tasks.add_task() calls
- asyncio.create_task() in control plane code
- threading imports or usage
- Long-running loops in route handlers
- Any sleep() or delay() calls in routes

Files to check:
- domain_expansion/app/routers/ops.py
- domain_expansion/app/routers/*.py (all router files)
- domain_expansion/main.py
- domain_expansion/app/integrations/*.py

Rules:
- Control plane endpoints must return quickly (under 5-10 seconds)
- All heavy work must be delegated to runner service
- Control plane only: creates ops_job row, calls runner with short timeout, updates ops_job status, returns

Actions if found:
- Remove BackgroundTasks usage
- Remove asyncio.create_task from control plane
- Ensure endpoints call runner and return immediately
- Runner handles all async execution

Acceptance criteria:
- No background execution is initiated from Vercel routes
- All control plane endpoints return within timeout limits
- All heavy work is delegated to runner

---

## Part 4 — Migrations or bootstrap (required)

### Step 11: Choose and implement schema creation

Option A: Alembic (preferred long-term)

Install: pip install alembic

Initialize: alembic init alembic

File: alembic/env.py
- Import engine from domain_expansion.app.db.session
- Import Base from domain_expansion.app.db.base
- Import all models from domain_expansion.app.models.ops
- Set target_metadata = Base.metadata
- Update run_migrations_online to use engine from session

File: alembic.ini
- Leave sqlalchemy.url empty (use engine from session.py)

Create initial migration:
- Command: alembic revision --autogenerate -m "Initial migration: ops_jobs and ops_job_events"
- Review generated migration file in alembic/versions/
- Ensure it creates ops_jobs table with all required fields
- Ensure it creates ops_job_events table (optional)
- Ensure it adds indexes: (status, created_at), (job_type, created_at)
- Ensure it uses UUID for id, JSONB for payload/result, proper timestamps

Run migration: alembic upgrade head

Option B: Idempotent bootstrap script (faster path)

File: scripts/bootstrap_schema.py (create new file)

Script contents:
- Import Base from domain_expansion.app.db.base
- Import engine from domain_expansion.app.db.session
- Import all models from domain_expansion.app.models.ops
- Call Base.metadata.create_all(bind=engine)
- Print success message

Script must be:
- Manually invoked only
- Never triggered by API requests
- Idempotent (safe to run multiple times)

### Step 12: Document migration commands

File: docs/ops/checklist_v2.md

Add section: Database Migrations

If using Alembic:
- Command to create migration: alembic revision --autogenerate -m "description"
- Command to apply: alembic upgrade head
- Command to rollback: alembic downgrade -1
- Note: migrations not run automatically on Vercel
- Note: run migrations manually after deployment

If using bootstrap script:
- Command to run: python scripts/bootstrap_schema.py
- Note: for initial setup only
- Note: use Alembic for ongoing migrations

Acceptance criteria:
- Clean Postgres database can be brought to required schema state using documented command
- Deploy does not depend on manual psql editing
- Schema creation is repeatable and idempotent

---

## Part 5 — ops_jobs model normalization (required)

### Step 13: Verify ops_jobs model types

File: domain_expansion/app/models/ops.py

Ensure OpsJob model has:
- id field: UUID primary key with server_default using gen_random_uuid()
- payload field: JSONB type (not JSON)
- result field: JSONB type (not JSON)
- created_at field: timezone-aware, server_default using now()
- updated_at field: timezone-aware, server_default using now(), onupdate set
- status field: Enum type (JobStatus enum)

### Step 14: Verify indexes exist

File: domain_expansion/app/models/ops.py

Ensure __table_args__ includes:
- Index on (status, created_at) descending
- Index on (job_type, created_at) descending

### Step 15: Update list endpoint with limits

File: domain_expansion/app/routers/ops.py

In list_jobs function:
- Default limit parameter: 50
- Hard cap: 200 (enforce maximum)
- Minimum: 1 (enforce minimum, default to 50 if invalid)

Add validation:
- If limit > 200, set limit = 200
- If limit < 1, set limit = 50

Acceptance criteria:
- Model reflects Postgres-first types (UUID, JSONB, timezone-aware timestamps)
- List endpoint cannot dump unlimited rows
- Default and hard cap limits are enforced

---

## Part 6 — Runner hardening (required)

### Step 16: Bound result and error sizes

File: runner/main.py

In _execute_job_async function:

Before writing result to database:
- Serialize result to JSON
- Check JSON string length
- If length > 10000 characters, replace with truncated message: {"error": "Result too large", "truncated": true}

Before writing error to database:
- Truncate error string to maximum 500 characters
- Use string slicing: error_msg = str(e)[:500]

Ensure updates happen in finally blocks:
- Success case: update status to succeeded with result
- Failure case: update status to failed with error
- Both cases must update ops_jobs in finally block to guarantee update

### Step 17: Update cancel semantics

File: domain_expansion/app/routers/ops.py

In cancel_job function:
- Set status to indicate cancellation intent
- Options: add CANCEL_REQUESTED to JobStatus enum, or set error field to "Cancellation requested by user"
- Do not claim cancellation stops running jobs
- Document that runner may honor cancellation if it checks periodically
- Return message: "Cancellation intent recorded"

Acceptance criteria:
- Runner never fails to update ops_jobs terminal state due to serialization size issues
- Error text is bounded to 500 characters
- Result JSON is bounded to 10KB
- Cancel endpoint is "intent only" unless explicit checks exist in runner

---

## Part 7 — Validation steps (must be done in this batch)

### Step 18: Add local validation steps to checklist

File: docs/ops/checklist_v2.md

Add section: Local Validation Steps

Include these test scenarios:

Control plane startup failure cases:
- Missing DATABASE_URL: app should fail immediately at startup
- Invalid DATABASE_URL (SQLite): app should fail immediately at startup
- Missing OPS_API_KEY in production: app should fail or warn appropriately

Runner startup failure cases:
- Missing DATABASE_URL: runner should fail immediately at startup
- Missing RUNNER_TOKEN: runner should fail immediately at startup

Happy path:
- Create job via POST /api/ops/jobs with X-Ops-Key header
- Trigger runner via POST /api/ops/trigger_runner
- Verify job transitions: queued → running → succeeded
- Check ops_jobs table in database for correct status updates

Unauthorized path:
- Request to /api/ops/jobs without X-Ops-Key header
- Expected: 401 response with "Invalid or missing X-Ops-Key" message

Secret leakage check:
- Check all /api/ops/* endpoint responses
- Verify no token values appear in responses
- Verify no runner URL appears in responses
- Use grep to search response bodies for token patterns

---

## Files to create or modify summary

New files:
- domain_expansion/app/dependencies.py
- scripts/bootstrap_schema.py (if Option B chosen)
- alembic.ini and alembic/ directory (if Option A chosen)

Modified files:
- domain_expansion/app/settings.py
- domain_expansion/app/routers/ops.py
- domain_expansion/app/integrations/runner_client.py
- runner/main.py
- runner/settings.py
- config/env.example
- docs/ops/checklist_v2.md

---

## Key file paths reference

Control plane settings: domain_expansion/app/settings.py
Ops router: domain_expansion/app/routers/ops.py
Runner settings: runner/settings.py
Runner execute endpoint: runner/main.py
Ops jobs model: domain_expansion/app/models/ops.py
Runner client: domain_expansion/app/integrations/runner_client.py
Env example: config/env.example
Checklist: docs/ops/checklist_v2.md
