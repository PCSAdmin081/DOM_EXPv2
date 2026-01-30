# Fixtures

This directory contains reference data files and fixtures for DOM_EXPANSION.

## Files

- `metrics_import_ready_v1.csv` — V1 metrics import CSV (reference schema)
- `metrics_import_outdated_reference.csv` — Outdated version (if applicable)

## Intended Schema

The metrics import CSV should follow this structure:

- **Required columns**: `page_id`, `timestamp`, `followers`, `source`
- **Optional columns**: `likes`, `comments`, `shares`, `views`
- **Format**: CSV with header row
- **Timestamp format**: ISO 8601 or Unix timestamp

## Warnings

⚠️ **Never commit actual production data or secrets to this directory.**

⚠️ **These are reference files only** — do not use in production without validation.

⚠️ **V2 may use different schema** — check current implementation before importing.
