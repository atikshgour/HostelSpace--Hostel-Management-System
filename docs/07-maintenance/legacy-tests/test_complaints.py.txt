# Owner: Atiksh Gour | US-13 / TC-FR07-01 / SEC-03 | Sprint 4
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient

from apps.accounts.models import StudentProfile, User
from apps.student_services.models import (
    Complaint,
    ComplaintCategory,
    ComplaintTransition,
)
from apps.student_services.services import submit_complaint

pytestmark = pytest.mark.django_db


@pytest.fixture
def students():
    first = User.objects.create_user(username='synthetic-student-a', role=User.Role.STUDENT)
    second = User.objects.create_user(username='synthetic-student-b', role=User.Role.STUDENT)
    StudentProfile.objects.create(user=first, srn='SYNTHETIC-A', room='A-101')
    StudentProfile.objects.create(user=second, srn='SYNTHETIC-B', room='B-202')
    return first, second


@pytest.fixture
def category():
    return ComplaintCategory.objects.create(code='synthetic-repair', name='Synthetic repair')


def session_client(user):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)
    response = client.get('/api/complaint-categories/')
    assert response.status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
    return client


def assert_error(response, status, code):
    assert response.status_code == status
    assert set(response.data) == {'code', 'message', 'fields'}
    assert response.data['code'] == code
    assert 'no-store' in response['Cache-Control'].split(', ')


def test_submission_persists_open_complaint_and_creation_history(students, category):
    student = students[0]
    client = session_client(student)
    response = client.post('/api/complaints/', {
        'category': category.pk, 'description': '  Synthetic broken light  ',
    }, format='json')
    assert response.status_code == 201
    complaint = Complaint.objects.get(pk=response.data['id'])
    assert complaint.student_id == student.pk
    assert complaint.room == 'A-101'
    assert complaint.status == 'Open'
    assert complaint.description == 'Synthetic broken light'
    assert complaint.created_at is not None
    event = complaint.history.get()
    assert (event.actor_id, event.old_status, event.new_status) == (student.pk, '', 'Open')
    assert event.created_at is not None
    assert event.remarks == 'Complaint submitted.'
    # A new authenticated client proves the response was persisted, not cached UI state.
    refreshed = session_client(student).get(f'/api/complaints/{complaint.pk}/')
    assert refreshed.status_code == 200
    assert refreshed.data == response.data
    listing = client.get('/api/complaints/')
    assert listing.data['count'] == 1
    assert listing.data['results'][0] == response.data
    assert 'no-store' in response['Cache-Control'].split(', ')


@pytest.mark.parametrize('payload,field', [
    ({}, 'category'),
    ({'description': 'Repair'}, 'category'),
    ({'category': 'valid'}, 'description'),
    ({'category': 'valid', 'description': ''}, 'description'),
    ({'category': 'valid', 'description': ' \n\t'}, 'description'),
    ({'category': 'valid', 'description': 'x' * 2001}, 'description'),
    ({'category': 'valid', 'description': None}, 'description'),
    ({'category': 'valid', 'description': 123}, 'description'),
    ({'category': 'valid', 'description': ['Repair']}, 'description'),
    ({'category': -1, 'description': 'Repair'}, 'category'),
    ({'category': 999999, 'description': 'Repair'}, 'category'),
    ({'category': 1.2, 'description': 'Repair'}, 'category'),
    ({'category': True, 'description': 'Repair'}, 'category'),
    ({'category': 'valid', 'description': 'Repair', 'room': 'B-202'}, 'room'),
    ({'category': 'valid', 'description': 'Repair', 'student': 42}, 'student'),
    ({'category': 'valid', 'description': 'Repair', 'status': 'Resolved'}, 'status'),
    ({'category': 'valid', 'description': 'Repair', 'history': []}, 'history'),
    ({'category': 'valid', 'description': 'Repair', 'assigned_to': 42}, 'assigned_to'),
])
def test_invalid_or_forged_fields_create_nothing(students, category, payload, field):
    payload = dict(payload)
    if payload.get('category') == 'valid':
        payload['category'] = category.pk
    response = session_client(students[0]).post('/api/complaints/', payload, format='json')
    assert_error(response, 400, 'validation_error')
    assert field in response.data['fields']
    assert not Complaint.objects.exists()
    assert not ComplaintTransition.objects.exists()


def test_maximum_description_length_is_accepted(students, category):
    response = session_client(students[0]).post('/api/complaints/', {
        'category': category.pk, 'description': 'x' * 2000,
    }, format='json')
    assert response.status_code == 201


def test_inactive_categories_are_hidden_and_rejected(students, category):
    category.is_active = False
    category.save()
    client = session_client(students[0])
    assert client.get('/api/complaint-categories/').data['results'] == []
    response = client.post('/api/complaints/', {
        'category': category.pk, 'description': 'Synthetic repair',
    }, format='json')
    assert_error(response, 400, 'validation_error')
    assert not Complaint.objects.exists()


@pytest.mark.parametrize('missing_profile', [False, True])
def test_missing_profile_or_room_is_rejected(students, category, missing_profile):
    profile = students[0].student_profile
    if missing_profile:
        profile.delete()
    else:
        profile.room = ' \t'
        profile.save()
    response = session_client(students[0]).post('/api/complaints/', {
        'category': category.pk, 'description': 'Synthetic repair',
    }, format='json')
    assert_error(response, 400, 'validation_error')
    assert 'room' in response.data['fields']
    assert not Complaint.objects.exists()


def test_students_only_see_their_own_records(students, category):
    own = submit_complaint(student=students[0], category=category, description='Own synthetic record')
    other = submit_complaint(student=students[1], category=category, description='Private synthetic record')
    client = session_client(students[0])
    response = client.get('/api/complaints/')
    assert response.data['count'] == 1
    assert [item['id'] for item in response.data['results']] == [own.pk]
    assert_error(client.get(f'/api/complaints/{other.pk}/'), 404, 'not_found')
    assert_error(client.get('/api/complaints/999999/'), 404, 'not_found')


@pytest.mark.parametrize('method', ['put', 'patch', 'delete'])
def test_students_cannot_modify_own_or_other_complaints(students, category, method):
    for student in students:
        complaint = submit_complaint(student=student, category=category, description='Synthetic record')
        client = session_client(students[0])
        response = getattr(client, method)(
            f'/api/complaints/{complaint.pk}/', {'status': 'Resolved'}, format='json',
        )
        assert_error(response, 405, 'method_not_allowed')
        complaint.refresh_from_db()
        assert complaint.status == 'Open'
        assert complaint.history.count() == 1


@pytest.mark.parametrize('path', ['/api/complaints/', '/api/complaints/1/', '/api/complaint-categories/'])
def test_anonymous_requests_are_401(path):
    assert_error(APIClient().get(path), 401, 'not_authenticated')


@pytest.mark.parametrize('role', [value for value, _ in User.Role.choices if value != User.Role.STUDENT])
def test_all_non_student_roles_are_denied_even_for_superusers(category, role):
    user = User.objects.create_user(username='synthetic-staff', role=role, is_superuser=True)
    client = APIClient()
    client.force_login(user)
    assert_error(client.get('/api/complaints/'), 403, 'permission_denied')
    assert_error(client.post('/api/complaints/', {
        'category': category.pk, 'description': 'Synthetic repair',
    }, format='json'), 403, 'permission_denied')
    assert not Complaint.objects.exists()


def test_inactive_account_and_changed_role_revoke_access(students):
    client = session_client(students[0])
    User.objects.filter(pk=students[0].pk).update(role=User.Role.MAINTENANCE)
    assert_error(client.get('/api/complaints/'), 403, 'permission_denied')
    User.objects.filter(pk=students[0].pk).update(is_active=False)
    assert_error(client.get('/api/complaints/'), 401, 'not_authenticated')


def test_real_session_post_requires_csrf(students, category):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(students[0])
    payload = {'category': category.pk, 'description': 'Synthetic repair'}
    assert_error(client.post('/api/complaints/', payload, format='json'), 403, 'permission_denied')
    assert not Complaint.objects.exists()
    client.get('/api/complaint-categories/')
    token = client.cookies[settings.CSRF_COOKIE_NAME].value
    response = client.post('/api/complaints/', payload, format='json', HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 201


def test_tracking_reflects_database_status_and_preserves_room_snapshot(students, category):
    complaint = submit_complaint(student=students[0], category=category, description='Synthetic repair')
    StudentProfile.objects.filter(user=students[0]).update(room='A-303')
    # Simulate state persisted by a future staff module; this story exposes no update API.
    Complaint.objects.filter(pk=complaint.pk).update(status=Complaint.Status.IN_PROGRESS)
    response = session_client(students[0]).get(f'/api/complaints/{complaint.pk}/')
    assert response.data['status'] == 'In Progress'
    assert response.data['room'] == 'A-101'
    next_complaint = submit_complaint(student=students[0], category=category, description='Next record')
    assert next_complaint.room == 'A-303'


def test_pagination_is_stable_and_scoped(students, category):
    for index in range(21):
        submit_complaint(student=students[0], category=category, description=f'Synthetic {index}')
    submit_complaint(student=students[1], category=category, description='Other student')
    client = session_client(students[0])
    first = client.get('/api/complaints/')
    second = client.get('/api/complaints/?page=2')
    assert first.data['count'] == second.data['count'] == 21
    first_ids = {item['id'] for item in first.data['results']}
    second_ids = {item['id'] for item in second.data['results']}
    assert len(first_ids) == 20
    assert len(second_ids) == 1
    assert not first_ids & second_ids


def test_submission_rolls_back_when_history_insert_fails(students, category):
    with patch.object(ComplaintTransition.objects, 'create', side_effect=RuntimeError('synthetic failure')):
        with pytest.raises(RuntimeError):
            submit_complaint(student=students[0], category=category, description='Synthetic repair')
    assert not Complaint.objects.exists()
    assert not ComplaintTransition.objects.exists()


def test_service_rechecks_authoritative_user_and_category(students, category):
    student = students[0]
    User.objects.filter(pk=student.pk).update(is_active=False)
    with pytest.raises(PermissionDenied):
        submit_complaint(student=student, category=category, description='Synthetic repair')
    User.objects.filter(pk=student.pk).update(is_active=True)
    ComplaintCategory.objects.filter(pk=category.pk).update(is_active=False)
    with pytest.raises(ValidationError):
        submit_complaint(student=student, category=category, description='Synthetic repair')
    assert not Complaint.objects.exists()


@pytest.mark.parametrize('field,value', [('description', ' \t'), ('room', ''), ('status', 'Invalid')])
def test_postgresql_constraints_reject_invalid_records(students, category, field, value):
    values = dict(student=students[0], category=category, room='A-101', description='Synthetic repair')
    values[field] = value
    with pytest.raises(IntegrityError), transaction.atomic():
        Complaint.objects.create(**values)


def test_history_cannot_be_rewritten_or_deleted(students, category):
    complaint = submit_complaint(student=students[0], category=category, description='Synthetic repair')
    event = complaint.history.get()
    event.remarks = 'Attempted rewrite'
    with pytest.raises(ModelValidationError):
        event.save()
    with pytest.raises(ModelValidationError):
        event.delete()
    with pytest.raises(ModelValidationError):
        complaint.history.update(remarks='Attempted rewrite')
    with pytest.raises(ModelValidationError):
        complaint.history.all().delete()
    with pytest.raises(ModelValidationError):
        complaint.history.bulk_update([event], ['remarks'])
    with pytest.raises(ProtectedError):
        complaint.delete()
    event.refresh_from_db()
    assert event.remarks == 'Complaint submitted.'


def test_profile_and_credentials_use_django_constraints_and_hashing(students):
    student = students[0]
    student.set_password('synthetic-password-only')
    student.save()
    assert student.password != 'synthetic-password-only'
    assert student.check_password('synthetic-password-only')
    client = APIClient()
    assert client.login(username=student.username, password='synthetic-password-only')
    assert client.get('/api/complaints/').status_code == 200
    with pytest.raises(IntegrityError), transaction.atomic():
        StudentProfile.objects.create(user=student, srn='SYNTHETIC-DUPLICATE', room='A-999')


@pytest.mark.parametrize('description', ['', ' \n', 'x' * 2001, None])
def test_service_validates_description_independently(students, category, description):
    with pytest.raises(ValidationError):
        submit_complaint(student=students[0], category=category, description=description)
    assert not Complaint.objects.exists()


def test_malformed_json_uses_standard_error_schema(students):
    response = session_client(students[0]).post(
        '/api/complaints/', data='{"broken":', content_type='application/json',
    )
    assert_error(response, 400, 'parse_error')
    assert not Complaint.objects.exists()


def test_unexpected_failure_is_sanitized_and_atomic(students, category):
    with patch.object(ComplaintTransition.objects, 'create', side_effect=RuntimeError('private sentinel')):
        response = session_client(students[0]).post('/api/complaints/', {
            'category': category.pk, 'description': 'Synthetic repair',
        }, format='json')
    assert_error(response, 500, 'server_error')
    assert 'private sentinel' not in str(response.data)
    assert not Complaint.objects.exists()


@pytest.mark.django_db(transaction=True)
def test_concurrent_submissions_keep_distinct_ids_and_complete_history(students, category):
    assert connection.vendor == 'postgresql'

    def submit(index):
        close_old_connections()
        try:
            return submit_complaint(
                student=students[0], category=category, description=f'Synthetic concurrent {index}',
            ).pk
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        identifiers = list(executor.map(submit, range(2)))
    assert len(set(identifiers)) == 2
    assert Complaint.objects.count() == ComplaintTransition.objects.count() == 2
    assert set(Complaint.objects.values_list('room', flat=True)) == {'A-101'}
