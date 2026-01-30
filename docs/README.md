# DOM_EXPv2 Documentation Index

This directory contains all documentation for DOM_EXPANSION v2.

## Authoritative V2 Contract

- **[Architecture V2 Contract](architecture/architecture_v2_contract.md)** — The authoritative source of truth for V2 system structure, contracts, and interaction patterns.

## Documentation Sections

### Operations
- [Setup (V1 Reference)](ops/setup_local_v1_reference.md) — V1 setup steps (reference only)
- [Deployment (V1 Reference)](ops/deployment_v1_reference.md) — V1 deployment guide (reference only)
- [Vercel Deployment (V1 Reference)](ops/vercel_deployment_v1_reference.md) — V1 Vercel deployment (reference only)
- [VPS Master Briefing (V1 Reference)](ops/vps_master_briefing_v1_reference.md) — V1 VPS strategy (reference only)
- [V2 Checklist](ops/checklist_v2.md) — V2 contract alignment checklist

### Environment
- [Environment Recovery Guide (V1)](env/env_recovery_guide_v1.md) — How to recover lost env values
- [Environment Recovery Summary (V1)](env/env_recovery_summary_v1.md) — Recovery process summary
- [Secrets Handling](env/SECRETS_HANDLING.md) — Rules for handling secrets

### Database
- [PCS DB README (V1 Reference)](db/pcs_db_readme_v1_reference.md) — V1 database documentation

### API
- (API documentation will be added here)

### Jobs
- (Job documentation will be added here)

### Nearsight
- [Nearsight Changelog (V1)](nearsight/changelog_v1.md) — V1 Nearsight changelog

### Captorator
- [Template Composition Briefing (V1)](captorator/template_composition_briefing_v1.md) — V1 Captorator template composition
- [Captorator Dev Log (V1)](captorator/dev_log_v1.md) — V1 Captorator development log

### Fixtures
- [Fixtures README](fixtures/README.md) — Reference data files and schemas

### History
- [V1 Changelog](history/v1_changelog.md) — Complete V1 changelog

### Reference (V1)
- [V1 README](reference_v1/readme_v1_reference.md) — V1 project README (reference only)

## What Not to Trust

⚠️ **V1 Deployment Steps** — V1 deployment instructions assume VPS hosting. V2 uses Vercel + runner.

⚠️ **SQLite References** — V2 is Postgres-only. Any SQLite references in V1 docs are outdated.

⚠️ **Scraping Instructions in Vercel** — V2 control plane (Vercel) does not execute long-running jobs. All heavy work is delegated to the runner service.

⚠️ **Scheduler in Vercel** — V1 docs may mention schedulers running in Vercel. V2 uses external cron or Vercel Cron Jobs to trigger endpoints.

## Quick Links

- **V2 Contract**: [Architecture V2 Contract](architecture/architecture_v2_contract.md)
- **V2 Checklist**: [V2 Alignment Checklist](ops/checklist_v2.md)
- **Secrets**: [Secrets Handling Guide](env/SECRETS_HANDLING.md)
