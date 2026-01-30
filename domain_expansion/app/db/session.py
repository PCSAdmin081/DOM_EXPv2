from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_expansion.app.settings import settings


def _normalize_db_url(url: str) -> str:
    # Accept postgres:// and normalize to postgresql://
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


DATABASE_URL = _normalize_db_url(str(settings.database_url))

# V2 invariant: Postgres only (fail fast)
if not DATABASE_URL.startswith("postgresql://"):
    raise RuntimeError(
        f"V2 requires DATABASE_URL to be postgresql:// (no SQLite fallback). "
        f"Got: {DATABASE_URL[:20]}... (truncated for security)"
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
