# Owner: Arin Singh | US-18 | Dev sprint 1 | SRS sprint 1 | Reviewer: Aryan Singh (pending)
import os

os.environ.setdefault("DJANGO_SECRET_KEY", "ci-only-not-for-deployment-02d45f99")
os.environ.setdefault(
    "HOSTELSPACE_SQLITE", "0"
)
from .base import *  # noqa: F403,E402

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
