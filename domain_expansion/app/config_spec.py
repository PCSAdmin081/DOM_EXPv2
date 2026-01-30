"""Contract-level config spec.

This file is intended to remain stable and be used by:
- settings validation
- scripts/audit_config.py
- scripts/repair_env.py

Do not read environment variables anywhere else.
"""

REQUIRED_CONTROL_PLANE_KEYS = [
    "APP_ENV",
    "DATABASE_URL",
    "SECRET_KEY",
]

FEATURE_FLAGS = [
    "NEARSIGHT_ENABLED",
    "CAPTORATOR_ENABLED",
    "JOBS_ENABLED",
    "NOTION_ENABLED",
    "RUNNER_ENABLED",
]

DEPRECATED_KEYS = [
    "SECONDARY_DATABASE_URL",
    "DATABASE_URL_SECONDARY",
    "VERCEL",
]
