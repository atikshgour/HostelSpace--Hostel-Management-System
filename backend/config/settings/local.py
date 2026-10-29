# Owner: Atiksh | US-20 foundation | Sprint 1
from .base import *  # noqa: F403

# US-14 same-origin Next.js development proxy. Production uses its reviewed origin.
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
