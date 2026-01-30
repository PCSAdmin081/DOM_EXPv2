# DOMAIN_EXPANSION (DOM_EXP) — V2

**V2 Contract-Aligned Implementation** for DOM_EXPv2.

## V2 Contract

The authoritative V2 contract is documented in **[docs/architecture/architecture_v2_contract.md](docs/architecture/architecture_v2_contract.md)**.

**Key V2 Principles:**
- **Control Plane** (Vercel): FastAPI app + UI + auth + Postgres-only + runner triggers
- **Runner** (self-hosted): FastAPI, no UI. Executes heavy jobs and writes to Postgres
- **Postgres-only**: No SQLite fallback — app crashes on startup if SQLite detected
- **No long jobs in Vercel**: All heavy work delegated to runner
- **Ops jobs logging**: All job execution logged in `ops_jobs` table
- **Runner token gating**: Runner requires `X-Runner-Token` header

## Documentation Index

See **[docs/README.md](docs/README.md)** for complete documentation index.

## Architecture
- **Control Plane** (Vercel): FastAPI app + UI + auth + Postgres (Supabase) + runner triggers.
- **Runner** (self-hosted): FastAPI, no UI. Executes heavy jobs on schedule and writes to Postgres.

## What this scaffold intentionally does NOT include
- No SQLite support.
- No Notion integration (feature-gated).
- No long-running jobs inside the control plane.
- No secrets or `.env` files (use env var manager).

## Quick start (local)
1. Set env vars (see `config/env.example`).
2. Run control plane:
   - `uvicorn domain_expansion.main:app --reload`
3. Run runner:
   - `uvicorn runner.main:app --reload --port 8010`

## Security / Secrets

⚠️ **Never commit `.env` values to the repository.**

- Use environment variable managers (Vercel Dashboard, local `.env` file)
- See [docs/env/SECRETS_HANDLING.md](docs/env/SECRETS_HANDLING.md) for rules
- Template files (`config/env.example`) contain keys only, no real values

## V2 Checklist

See [docs/ops/checklist_v2.md](docs/ops/checklist_v2.md) for V2 contract alignment checklist.
