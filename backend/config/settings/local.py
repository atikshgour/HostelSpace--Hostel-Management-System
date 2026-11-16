# Owner: Arin Singh | US-18 | Dev sprint 1 | SRS sprint 1 | Reviewer: Aryan Singh (pending)
"""Explicit local quick mode. Set HOSTELSPACE_SQLITE=0 and DATABASE_URL for PostgreSQL."""

import os
import secrets
from pathlib import Path

os.environ.setdefault("HOSTELSPACE_SQLITE", "1")
# Persist a generated development key locally; never use it in deployment.
key_file = Path(__file__).resolve().parents[2] / ".local-secret"
if not os.environ.get("DJANGO_SECRET_KEY"):
    if not key_file.exists():
        key_file.write_text(secrets.token_urlsafe(64))
        key_file.chmod(0o600)
    os.environ["DJANGO_SECRET_KEY"] = key_file.read_text().strip()
os.environ.setdefault(
    "DJANGO_CSRF_TRUSTED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
)
from .base import *  # noqa: F403,E402

DEBUG = True
