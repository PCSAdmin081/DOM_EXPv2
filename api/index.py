"""Vercel entrypoint.

Vercel expects an ASGI app exposed as `app`.
"""
from domain_expansion.main import app  # noqa: F401
