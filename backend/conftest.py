# Owner: Arin Singh | US-18 | Dev sprint 1 | SRS sprint 1 | Reviewer: Aryan Singh (pending)
"""Pytest bootstrap for the team backend."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.ci")
