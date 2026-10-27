"""Arin Singh | US-18 shared integration configuration.
Requires the team-owned accounts.User and information.Rule contracts.
"""
import os
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
BASE_DIR=Path(__file__).resolve().parents[2]
SECRET_KEY=os.environ['DJANGO_SECRET_KEY']
DEBUG=False
ALLOWED_HOSTS=[x.strip() for x in os.environ.get('DJANGO_ALLOWED_HOSTS','localhost,127.0.0.1').split(',') if x.strip()]
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','rest_framework','apps.accounts','apps.information','apps.leave_attendance']
AUTH_USER_MODEL='accounts.User'
HOSTELSPACE_RULE_MODEL='information.Rule'
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware']
ROOT_URLCONF='config.urls'
WSGI_APPLICATION='config.wsgi.application'
ASGI_APPLICATION='config.asgi.application'
database_url=urlparse(os.environ['DATABASE_URL'])
if database_url.scheme not in ('postgres','postgresql') or not database_url.hostname or not database_url.path.strip('/'):
    raise RuntimeError('DATABASE_URL must identify a PostgreSQL database.')
options=parse_qs(database_url.query)
sslmode=options.get('sslmode',['prefer'])[0]
if sslmode not in ('disable','allow','prefer','require','verify-ca','verify-full'):
    raise RuntimeError('Use a supported PostgreSQL SSL mode.')
DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':unquote(database_url.path.lstrip('/')),'USER':unquote(database_url.username or ''),'PASSWORD':unquote(database_url.password or ''),'HOST':database_url.hostname,'PORT':str(database_url.port or 5432),'OPTIONS':{'sslmode':sslmode}}}
DATA_UPLOAD_MAX_MEMORY_SIZE=65536

USE_TZ=True
TIME_ZONE='Asia/Kolkata'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
REST_FRAMEWORK={'DEFAULT_AUTHENTICATION_CLASSES':['rest_framework.authentication.SessionAuthentication'],'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.IsAuthenticated'],'EXCEPTION_HANDLER':'config.exceptions.api_exception_handler','DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'30/min','user':'300/min'}}
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE='Lax'
CSRF_COOKIE_SAMESITE='Lax'
CSRF_TRUSTED_ORIGINS=[x.strip() for x in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS','').split(',') if x.strip()]
from config.logging import LOGGING
