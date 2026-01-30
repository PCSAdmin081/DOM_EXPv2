# DOMAIN_EXPANSION VPS Master Briefing (V1 Reference)

> **REFERENCE ONLY** — V2 uses Vercel + runner; keep for infra/security conventions.

## Master Strategy & Build Briefing (VPS-Based)

## 0. Executive Intent

DOMAIN_EXPANSION is a privately hosted internal operations platform for
Pathway Connection Solutions / Overly Marketing Group. It consolidates:

-   Network-wide social metrics and analytics\
-   Internal content and data tools (Captorator, Nearsight)\
-   Program health, observability, and iteration velocity

The system is **internal-only**, **not WordPress-based**, and runs on a
**dedicated VPS** accessed via a secured subdomain.

------------------------------------------------------------------------

## 1. Hosting & Infrastructure Strategy

### 1.1 Hosting Model

-   Single VPS (Ubuntu LTS)
-   Always-on, stable environment
-   No mobile or consumer hardware dependencies

### 1.2 Network Access

-   Subdomain: `dashboard.pthwyconnect.com`
-   Ingress via Cloudflare Tunnel
-   TLS handled by Cloudflare
-   No direct inbound ports exposed

### 1.3 Security Boundary

-   Cloudflare Access for staff-only entry
-   App-level authentication and RBAC enforced internally

------------------------------------------------------------------------

## 2. System Architecture Overview

### 2.1 High-Level Architecture

    [ Staff Browser ]
            ↓
    [ Cloudflare Access + Tunnel ]
            ↓
    [ VPS ]
      ├─ FastAPI App (DOMAIN_EXPANSION)
      │    ├─ Dashboard
      │    ├─ Captorator
      │    ├─ Nearsight
      │    └─ Ops/Admin UI
      │
      ├─ Background Jobs
      ├─ SQLite DB
      └─ Persistent File Storage

### 2.2 Design Principles

-   Modular but integrated
-   Deterministic logic
-   Observability-first
-   Versioned APIs and schemas
-   Upgrade-safe

------------------------------------------------------------------------

## 3. Core Application Responsibilities

### 3.1 Dashboard

-   Network totals and growth deltas
-   Per-page metrics and graphs
-   Historical snapshots
-   Data freshness indicators

### 3.2 Metrics Ingestion

-   Collector-based ingestion
-   Scheduled background jobs
-   Idempotent snapshot writes
-   Historical time-series storage

------------------------------------------------------------------------

## 4. Captorator Integration

-   Route: `/tools/captorator`
-   API: `/api/v1/captorator/*`
-   Deterministic caption generation
-   Profile-driven presets
-   Logged runs and stored outputs

------------------------------------------------------------------------

## 5. Nearsight Integration

-   Route: `/tools/nearsight`
-   API: `/api/v1/nearsight/*`
-   Feed ingestion, filtering, scoring
-   Strong deduplication
-   Exportable outputs
-   Failure-tolerant job execution

------------------------------------------------------------------------

## 6. Authentication & Authorization

-   Username/password auth
-   Hashed credentials
-   RBAC roles:
    -   admin
    -   ops
    -   viewer

------------------------------------------------------------------------

## 7. Ops, Observability, and Stability

-   Ops UI for job status and manual runs
-   Structured logging
-   No silent failures
-   Dashboard-visible error states

------------------------------------------------------------------------

## 8. Data & Storage Strategy

### 8.1 Database

-   SQLite initially
-   Migration path to Postgres
-   UTC timestamps
-   Idempotent daily rows

### 8.2 File Storage

-   Persistent `./data/` directory
-   Subfolders: uploads, outputs, cache, logs

### 8.3 Backups

-   Nightly DB + output snapshots
-   Stored off-VPS

------------------------------------------------------------------------

## 9. Configuration & Secrets

-   Environment-variable driven
-   `.env.example` provided
-   No secrets committed

------------------------------------------------------------------------

## 10. Development & Deployment

-   Local development first
-   Git-based deployment
-   Simple restart strategy
-   Versioned APIs and migrations

------------------------------------------------------------------------

## 11. Non-Goals

-   Not WordPress
-   Not public-facing
-   Not mobile-hosted
-   Not a scheduling/posting system
-   Not multi-tenant (yet)

------------------------------------------------------------------------

## 12. Definition of Success

-   Stable staff access via subdomain
-   Accurate, trustworthy metrics
-   Reliable Captorator and Nearsight tools
-   Easy iteration without infra friction

------------------------------------------------------------------------

## Bottom Line

DOMAIN_EXPANSION is a **VPS-first internal platform** designed to scale
operational capability without platform compromises.
