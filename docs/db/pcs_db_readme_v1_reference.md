# PCS Dashboard v2.0 (Modular Monorepo)

This repository contains the modular PCS Dashboard stack.

## Modules
- `api/` — FastAPI gateway exposing `/api/v2/*`
- `portal/` — Next.js 14 dashboard
- `modules/oracle-scraper/` — IG data ingestion
- `modules/live-metrics/` — ETL, rollups, projections
- `modules/template-composer/` — Caption and image composition
- `shared/` — JSON Schemas + generated types and shared libs
- `infra/` — Compose and Docker config

## Quick start
```bash
# 1) Copy .env.example to .env and set secrets
cp .env.example .env

# 2) Start services
make dev

# 3) Open the portal
# http://localhost:3000
```
