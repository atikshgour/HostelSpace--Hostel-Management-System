# Owner: Atiksh | US-20 foundation; US-14 CSRF proxy | Sprint 1
import os

from .base import *  # noqa: F403

# US-14 same-origin Next.js development proxy. Production uses its reviewed origin.
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000',
).split(',')
