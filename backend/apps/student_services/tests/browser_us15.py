# Owner: Atiksh Gour | US-15 / TC-FR08-01 | Sprint 5 | Reviewer: Anvi Srinivas
# Opt-in browser check: local Node/Chrome and frontend dependencies required.
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

pytest_plugins = ['apps.student_services.tests.test_mess']


@pytest.fixture
def mess_live_server(settings):
    settings.STATIC_URL = '/static/'
    settings.MEDIA_URL = '/media/'
    settings.CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:3315']
    server = LiveServer('localhost')
    yield server
    server.stop()


@pytest.mark.django_db(transaction=True)
def test_us15_browser_workflow(users, mess_live_server, settings):
    root = Path(__file__).resolve().parents[4]
    (root / '.local').mkdir(exist_ok=True)
    origin = 'http://127.0.0.1:3315'
    sessions = {}
    for name, user in users.items():
        client = APIClient()
        client.force_login(user)
        sessions[name] = client.cookies[settings.SESSION_COOKIE_NAME].value
    environment = {**os.environ, 'DJANGO_API_URL': mess_live_server.url, 'NEXT_TELEMETRY_DISABLED': '1'}
    with (root / '.local/us15-next-browser.log').open('w', encoding='utf-8') as log:
        server = subprocess.Popen(
            ['node', 'node_modules/next/dist/bin/next', 'dev', '--hostname', '127.0.0.1', '--port', '3315'],
            cwd=root / 'frontend', env=environment, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(60):
                try:
                    with urlopen(origin + '/mess', timeout=2) as response:
                        if response.status == 200:
                            break
                except (URLError, TimeoutError):
                    time.sleep(0.5)
            else:
                pytest.fail('Next.js did not start; inspect the ignored browser log.')
            result = subprocess.run(
                ['node', 'e2e/us15-browser.mjs'], cwd=root / 'frontend', env=environment,
                input=json.dumps({'origin': origin, 'sessions': sessions, 'student': users['student'].pk}),
                capture_output=True, text=True, timeout=120,
            )
            assert result.returncode == 0, result.stderr
            assert 'US-15 browser workflow passed' in result.stdout
        finally:
            server.terminate()
            try:
                server.wait(timeout=15)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
