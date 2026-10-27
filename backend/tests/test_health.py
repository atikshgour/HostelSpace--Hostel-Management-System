# Owner: Atiksh | US-20 / TC-CICD-01 | Sprint 1
from unittest.mock import patch

import pytest
from django.db import OperationalError, connection
from django.test import Client


@pytest.mark.django_db
def test_health_checks_postgresql():
    assert connection.vendor == 'postgresql'
    response = Client().get('/api/health/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
    assert 'no-store' in response['Cache-Control'].split(', ')


def test_database_failure_is_unavailable_without_details():
    with patch('config.health.connection.cursor', side_effect=OperationalError('private')):
        response = Client().get('/api/health/')
    assert response.status_code == 503
    assert response.json() == {
        'code': 'unavailable', 'message': 'Database unavailable', 'fields': {},
    }
    assert 'no-store' in response['Cache-Control'].split(', ')


def test_health_rejects_writes_without_querying_database():
    with patch('config.health.connection.cursor') as cursor:
        response = Client().post('/api/health/')
    assert response.status_code == 405
    cursor.assert_not_called()
