"""Idempotent schema bootstrap script.

Run this once per environment to create required tables.
Safe to run multiple times (idempotent).

Usage:
    python scripts/bootstrap_schema.py

Note: This is for initial setup only. For ongoing migrations, use Alembic.
"""

from domain_expansion.app.db.base import Base
from domain_expansion.app.db.session import get_engine
from domain_expansion.app.models.ops import OpsJob, OpsJobEvent

if __name__ == "__main__":
    print("Creating tables...")
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print("Schema bootstrap complete.")
    print("Note: For ongoing migrations, use Alembic instead of this script.")
