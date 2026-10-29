# Owner: Atiksh Gour | US-14 | Sprint 4 | Reviewer: Anvi Srinivas
# Explicit opt-in integration check: requires frontend dependencies and local Chrome.
import json
import os
import subprocess
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from pytest_django.live_server_helper import LiveServer
from rest_framework.test import APIClient

pytest_plugins = ['apps.student_services.tests.test_complaint_management']


@pytest.fixture(autouse=True)
def browser_settings(settings):
    # The minimal scaffold does not yet configure static/media URL prefixes.
    settings.STATIC_URL = '/static/'
    settings.MEDIA_URL = '/media/'
    settings.CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:3314']


@pytest.fixture
def complaint_live_server(browser_settings):
    server = LiveServer('localhost')
    yield server
    server.stop()


@pytest.mark.django_db(transaction=True)
def test_us14_browser_workflow(records, complaint_live_server, settings):
    root = Path(__file__).resolve().parents[4]
    frontend = root / 'frontend'
    users, complaint = records
    origin = 'http://127.0.0.1:3314'
    settings.CSRF_TRUSTED_ORIGINS = [origin]
    sessions = {}
    for name, user in users.items():
        client = APIClient()
        client.force_login(user)
        sessions[name] = client.cookies[settings.SESSION_COOKIE_NAME].value
    environment = {**os.environ, 'DJANGO_API_URL': complaint_live_server.url, 'NEXT_TELEMETRY_DISABLED': '1'}
    log_path = root / '.local' / 'us14-next-browser.log'
    with log_path.open('w', encoding='utf-8') as log:
        server = subprocess.Popen(
            ['node', 'node_modules/next/dist/bin/next', 'dev', '--hostname', '127.0.0.1', '--port', '3314'],
            cwd=frontend, env=environment, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(60):
                try:
                    with urlopen(origin + '/complaints/manage', timeout=2) as response:
                        if response.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.5)
            else:
                pytest.fail('Next.js did not start; inspect the ignored local browser log.')
            result = subprocess.run(
                ['node', 'e2e/us14-browser.mjs'], cwd=frontend, env=environment,
                input=json.dumps({'origin': origin, 'sessions': sessions,
                                  'complaint': complaint.pk, 'staff': users['staff'].pk}),
                capture_output=True, text=True, timeout=120,
            )
            assert result.returncode == 0, result.stderr
            assert 'US-14 browser workflow passed' in result.stdout
            complaint.refresh_from_db()
            assert complaint.status == 'Resolved'
            assert complaint.assigned_to_id == users['staff'].pk
            assert complaint.history.count() == 4
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
