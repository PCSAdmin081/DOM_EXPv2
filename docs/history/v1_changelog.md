# Changelog

## [1.1.0] - 2025-01-XX - VPS Deployment Strategy

### Changed
- **Deployment Strategy**: Updated to VPS-first approach (dedicated Ubuntu LTS VPS)
- **Access Method**: Configured for `dashboard.pthwyconnect.com` via Cloudflare Tunnel
- **Security**: Added Cloudflare Access integration for staff-only authentication
- **Documentation**: Comprehensive VPS deployment guide added (DEPLOYMENT.md)
- **Backup Strategy**: Added nightly automated backup system
- **Deployment Workflow**: Added git-based deployment process

### Added
- `DEPLOYMENT.md`: Complete VPS deployment guide with:
  - Cloudflare Tunnel setup
  - Cloudflare Access configuration
  - Systemd service configuration
  - Backup automation
  - Git-based deployment workflow
  - PostgreSQL migration path
- Backup script template for off-VPS storage
- Deployment script for git-based updates

### Updated
- README.md: Emphasizes VPS-first strategy
- SETUP.md: Updated with VPS deployment references
- Removed emphasis on Termux/Android deployment (moved to local dev only)

### Technical Details
- App binds to `127.0.0.1` by default (safe for Cloudflare Tunnel)
- No direct inbound ports required
- TLS handled by Cloudflare
- Session cookies configured for HTTPS when `SESSION_COOKIE_SECURE=true`

## [1.0.0] - 2025-01-XX

### Added
- Initial release of DOMAIN_EXPANSION unified dashboard
- Authentication system with role-based access control (admin, ops, viewer)
- Dashboard with network overview and per-page metrics
- Captorator module integration
- Nearsight scraper module (Python port)
- Background job scheduler (APScheduler)
- Admin and Ops pages for system management
- SQLite database with migration-ready structure
- Dark theme UI with responsive design
- API versioning (/api/v1/)
- Session management with secure cookies
- Job run history and audit logging

### Technical Details
- FastAPI backend
- SQLAlchemy ORM with SQLite (PostgreSQL-ready)
- Jinja2 templates for server-rendered UI
- Chart.js for data visualization
- Modular architecture for easy updates

### Known Limitations
- Metrics collection job is a stub (needs implementation)
- Nearsight scoring logic simplified from original TypeScript version
- Chart visualization needs time series data population
- Some error handling could be more robust

### Future Enhancements
- Google Workspace SSO integration
- PostgreSQL migration support
- Enhanced metrics collection from platform APIs
- More sophisticated Nearsight scoring
- Real-time updates via WebSockets
- Export functionality for reports

## [1.2.0] - 2026-01-29 - Database Hardening, Configuration Management, and Content Routing

### Changed
- **Database Configuration**: Enforced Supabase/Postgres-only operation using a single canonical `DATABASE_URL` and removed SQLite fallback behavior
- **Schema Management**: Added safe `search_path` handling with schema name validation and defaulting to `public` if invalid
- **Connection Pooling**: Added serverless-safe SQLAlchemy connection pooling settings (`pool_pre_ping`, `pool_recycle`, `pool_size`, `max_overflow`, `pool_timeout`) to reduce stale DB connection failures
- **Notion Integration**: Made Notion integration disabled by default and gated router registration behind `NOTION_ENABLED` feature flag
- **Scheduler Control**: Removed direct environment variable usage of `VERCEL` and `DISABLE_SCHEDULER` and standardized scheduling control via `SCHEDULER_ENABLED` setting
- **Metrics Storage**: Deprecated legacy metrics naming and standardized metrics storage on the `metrics_snapshots` table

### Added
- **Feature Flags**: Added `NEARSIGHT_ENABLED`, `CAPTORATOR_ENABLED`, and `JOBS_ENABLED` to gate feature behavior and required tables
- **Ops Job Tracking**: Added `ops_jobs` table/model and related schema-guard support for tracking internal ops/runner jobs
- **Startup Validation**: Added a startup contract guard (`contract_guard.py`) to validate required tables and detect route prefix/duplicate-path issues early
- **Configuration Audit**: Extended the audit script (`scripts/audit_config.py`) to inventory env var usage and detect raw SQL table-name mismatches against model table names
- **Runner Integration**: Added runner integration (settings + client) so the dashboard can trigger secured jobs on a separate host
- **Ops Dashboard**: Added an `/ops/clawdbot` dashboard page to run ops jobs and view recent job results
- **Standalone Runner Service**: Added a standalone runner FastAPI service (`runner/main.py`) with token auth and allowlisted job types for executing analysis jobs
- **Nearsight Event Candidates**: Implemented Nearsight "event candidates" UI and endpoints for listing candidates and approving/rejecting them
- **Content Opportunities Router**: Upgraded Nearsight candidate generation into a deterministic "content opportunities router" that assigns region, category, target pages, score, and usage angles
- **Nearsight Scheduling**: Added Nearsight pipeline scheduling for quarter-hour runs (07:00–22:00 America/New_York) plus a manual `run_now` endpoint and UI button that does not affect scheduled runs
- **Routing Policy Module**: Added Nearsight routing policy module (`nearsight/routing_policy.py`) with regions, categories, and page weights as an operator-editable configuration surface

### Technical Details
- Database URL canonicalization checks `SQLALCHEMY_DATABASE_URL`, `DATABASE_URL`, `POSTGRES_URL`, `POSTGRES_PRISMA_URL` in order
- Schema guard runs once at startup (not per-request) and is fully idempotent
- Contract guard validates table name uniqueness, required tables in models, tables in database, and router prefix contracts
- Configuration audit script uses AST parsing to detect env var usage and compares against `config_spec.py`
- Runner service requires `X-Runner-Token` header and only executes allowlisted job types
- Nearsight routing uses deterministic keyword matching and scoring (no LLMs) with explainable signals
- Pipeline includes concurrency protection to prevent overlapping runs
