from .base import *
if not os.environ.get('DJANGO_ALLOWED_HOSTS') or not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
    raise RuntimeError('Set explicit deployment hostnames.')
if len(SECRET_KEY)<50 or SECRET_KEY.startswith('local-'):
    raise RuntimeError('Provide a strong deployment-only secret.')
if not CSRF_TRUSTED_ORIGINS or any(not x.startswith('https://') for x in CSRF_TRUSTED_ORIGINS):
    raise RuntimeError('Set explicit HTTPS CSRF origins.')
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_CONTENT_TYPE_NOSNIFF=True
# Configure SECURE_PROXY_SSL_HEADER only after Atiksh validates a trusted proxy.

if DATABASES['default']['OPTIONS']['sslmode'] not in ('require','verify-ca','verify-full'):
    raise RuntimeError('Require encrypted PostgreSQL transport in production.')
