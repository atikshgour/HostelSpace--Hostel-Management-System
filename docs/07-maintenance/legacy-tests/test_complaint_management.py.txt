# Owner: Atiksh Gour | US-14 / TC-FR07-01 / SEC-01 | Sprint 4 | Reviewer: Anvi Srinivas
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import close_old_connections, connection
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient

from apps.accounts.models import StudentProfile, User
from apps.student_services.models import (
    ComplaintCategory,
    ComplaintTransition,
)
from apps.student_services.services import (
    advance_complaint,
    assign_complaint,
    submit_complaint,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def records():
    users = {}
    for name, role in [('director', User.Role.HOSTEL_DIRECTOR), ('staff', User.Role.MAINTENANCE),
                       ('other', User.Role.MAINTENANCE), ('student', User.Role.STUDENT)]:
        users[name] = User.objects.create_user(username=f'synthetic-{name}', role=role)
    StudentProfile.objects.create(user=users['student'], srn='SYNTHETIC-US14', room='A-1')
    category = ComplaintCategory.objects.create(code='synthetic-us14', name='Synthetic repair')
    complaint = submit_complaint(student=users['student'], category=category, description='Synthetic light')
    return users, complaint


def client_for(user):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)
    response = client.get('/api/complaints/manage/')
    assert response.status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
    return client


def assign(users, complaint, staff='staff'):
    return assign_complaint(actor=users['director'], complaint_id=complaint.pk,
                            assigned_to=users[staff], remarks='Synthetic assignment')


def advance(users, complaint, actor='staff', old='Open', new='In Progress'):
    return advance_complaint(actor=users[actor], complaint_id=complaint.pk,
                             expected_status=old, status=new, remarks='Synthetic progress')


def test_director_assigns_staff_and_full_progress_is_visible_to_student(records):
    users, complaint = records
    director = client_for(users['director'])
    response = director.get('/api/maintenance-staff/')
    assert {u['id'] for u in response.data['results']} == {users['staff'].pk, users['other'].pk}
    response = director.post(f'/api/complaints/{complaint.pk}/assign/', {
        'assigned_to': users['staff'].pk, 'remarks': '  Synthetic assignment  ',
    }, format='json')
    assert response.status_code == 200
    assert response.data['assigned_to'] == users['staff'].pk
    staff = client_for(users['staff'])
    assert staff.get('/api/complaints/manage/').data['count'] == 1
    assert not staff.get('/api/complaints/manage/').data['can_assign']
    for old, new in [('Open', 'In Progress'), ('In Progress', 'Resolved')]:
        response = staff.post(f'/api/complaints/{complaint.pk}/progress/', {
            'expected_status': old, 'status': new, 'remarks': f'Synthetic {new}',
        }, format='json')
        assert response.status_code == 200
    student = APIClient()
    student.force_login(users['student'])
    response = student.get(f'/api/complaints/{complaint.pk}/')
    assert response.data['status'] == 'Resolved'
    history = response.data['history']
    assert len(history) == 4
    assert history[1]['old_status'] == history[1]['new_status'] == 'Open'
    assert history[1]['old_assigned_to'] is None
    assert history[1]['new_assigned_to'] == users['staff'].pk
    assert history[1]['actor'] == users['director'].pk
    assert history[1]['remarks'] == 'Synthetic assignment'
    assert all(h['created_at'] for h in history)
    assert history[-1]['actor'] == users['staff'].pk
    assert 'no-store' in response['Cache-Control']


@pytest.mark.parametrize('role', [User.Role.STUDENT, User.Role.WARDEN, User.Role.CHIEF_WARDEN,
                                  User.Role.MESS, User.Role.LAUNDRY])
def test_other_roles_denied_even_superusers(records, role):
    users, complaint = records
    user = User.objects.create_user(username='synthetic-forbidden', role=role, is_superuser=True)
    client = APIClient()
    client.force_login(user)
    assert client.get('/api/complaints/manage/').status_code == 403
    assert client.get('/api/maintenance-staff/').status_code == 403
    assert client.post(f'/api/complaints/{complaint.pk}/progress/', {}).status_code == 403
    assert client.post(f'/api/complaints/{complaint.pk}/assign/', {}).status_code == 403


def test_anonymous_inactive_and_csrf(records):
    users, complaint = records
    assert APIClient().get('/api/complaints/manage/').status_code == 401
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(users['director'])
    response = client.post(f'/api/complaints/{complaint.pk}/assign/', {
        'assigned_to': users['staff'].pk, 'remarks': 'Synthetic',
    }, format='json')
    assert response.status_code == 403
    assert set(response.data) == {'code', 'message', 'fields'}
    users['director'].is_active = False
    users['director'].save()
    assert client.get('/api/complaints/manage/').status_code == 401
    assert complaint.history.count() == 1


@pytest.mark.parametrize('payload', [
    {}, {'assigned_to': 'staff'}, {'assigned_to': 'staff', 'remarks': ''},
    {'assigned_to': 'staff', 'remarks': 'x' * 501},
    {'assigned_to': 'staff', 'remarks': 123},
    {'assigned_to': 'staff', 'remarks': 'Synthetic', 'status': 'Resolved'},
    {'assigned_to': 'student', 'remarks': 'Synthetic'},
    {'assigned_to': 999999, 'remarks': 'Synthetic'},
    {'assigned_to': True, 'remarks': 'Synthetic'},
])
def test_assignment_validation_no_changes(records, payload):
    users, complaint = records
    payload = dict(payload)
    if isinstance(payload.get('assigned_to'), str) and payload['assigned_to'] in users:
        payload['assigned_to'] = users[payload['assigned_to']].pk
    response = client_for(users['director']).post(
        f'/api/complaints/{complaint.pk}/assign/', payload, format='json',
    )
    assert response.status_code == 400
    complaint.refresh_from_db()
    assert complaint.assigned_to is None
    assert complaint.history.count() == 1


def test_assignment_rechecks_active_role_and_actor_from_db(records):
    users, complaint = records
    User.objects.filter(pk=users['staff'].pk).update(is_active=False)
    with pytest.raises(ValidationError):
        assign(users, complaint)
    User.objects.filter(pk=users['staff'].pk).update(is_active=True, role=User.Role.MESS)
    with pytest.raises(ValidationError):
        assign(users, complaint)
    User.objects.filter(pk=users['director'].pk).update(role=User.Role.STUDENT)
    with pytest.raises(PermissionDenied):
        assign(users, complaint)


def test_assignment_scope_and_reassignment_preserve_history(records):
    users, complaint = records
    assign(users, complaint)
    first = list(complaint.history.values())
    with pytest.raises(ValidationError):
        assign(users, complaint)
    other = client_for(users['other'])
    assert other.get('/api/complaints/manage/').data['count'] == 0
    payload = {'expected_status': 'Open', 'status': 'In Progress', 'remarks': 'Synthetic'}
    assert other.post(f'/api/complaints/{complaint.pk}/progress/', payload).status_code == 404
    assert other.post('/api/complaints/999999/progress/', payload).status_code == 404
    assert other.get('/api/maintenance-staff/').status_code == 403
    assert other.post(f'/api/complaints/{complaint.pk}/assign/', {}).status_code == 403
    assign(users, complaint, 'other')
    assert list(complaint.history.values())[:2] == first
    event = complaint.history.last()
    assert (event.old_assigned_to_id, event.new_assigned_to_id) == (users['staff'].pk, users['other'].pk)
    assert client_for(users['staff']).post(f'/api/complaints/{complaint.pk}/progress/', payload).status_code == 404


@pytest.mark.parametrize('old,new', [('Open', 'Resolved'), ('Open', 'Open'),
                                    ('In Progress', 'Open'), ('Resolved', 'Open'),
                                    ('Resolved', 'In Progress'), ('Resolved', 'Resolved')])
def test_no_skip_reverse_or_repeat(records, old, new):
    users, complaint = records
    assign(users, complaint)
    if old != 'Open':
        advance(users, complaint)
    if old == 'Resolved':
        advance(users, complaint, old='In Progress', new='Resolved')
    before = complaint.history.count()
    with pytest.raises(ValidationError):
        advance(users, complaint, old=old, new=new)
    complaint.refresh_from_db()
    assert complaint.status == old
    assert complaint.history.count() == before
    if old == 'Resolved':
        with pytest.raises(ValidationError):
            assign(users, complaint, 'other')


def test_director_progress_requires_assignment_and_stale_status_is_rejected(records):
    users, complaint = records
    with pytest.raises(ValidationError):
        advance(users, complaint, actor='director')
    assign(users, complaint)
    advance(users, complaint, actor='director')
    with pytest.raises(ValidationError):
        advance(users, complaint, actor='director')
    assert complaint.history.count() == 3


@pytest.mark.parametrize('operation', ['assign', 'progress'])
def test_history_failure_rolls_back_write(records, operation):
    users, complaint = records
    if operation == 'progress':
        assign(users, complaint)
    before = complaint.history.count()
    with patch.object(ComplaintTransition.objects, 'create', side_effect=RuntimeError('synthetic failure')):
        with pytest.raises(RuntimeError):
            (assign if operation == 'assign' else advance)(users, complaint)
    complaint.refresh_from_db()
    assert complaint.status == 'Open'
    assert complaint.assigned_to_id == (users['staff'].pk if operation == 'progress' else None)
    assert complaint.history.count() == before


@pytest.mark.parametrize('payload', [
    {}, {'status': 'In Progress', 'remarks': 'Synthetic'},
    {'expected_status': 'Open', 'status': 'invalid', 'remarks': 'Synthetic'},
    {'expected_status': 'Open', 'status': 'In Progress', 'remarks': ''},
    {'expected_status': 'Open', 'status': 'In Progress', 'remarks': 12},
    {'expected_status': 'Open', 'status': 'In Progress', 'remarks': 'x' * 501},
    {'expected_status': 'Open', 'status': 'In Progress', 'remarks': 'Synthetic', 'actor': 1},
])
def test_progress_input_rejected_without_history(records, payload):
    users, complaint = records
    assign(users, complaint)
    response = client_for(users['staff']).post(
        f'/api/complaints/{complaint.pk}/progress/', payload, format='json',
    )
    assert response.status_code == 400
    assert set(response.data) == {'code', 'message', 'fields'}
    complaint.refresh_from_db()
    assert complaint.status == 'Open'
    assert complaint.history.count() == 2


def test_staff_role_change_and_csrf_reject_progress(records):
    users, complaint = records
    assign(users, complaint)
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(users['staff'])
    payload = {'expected_status': 'Open', 'status': 'In Progress', 'remarks': 'Synthetic'}
    assert client.post(f'/api/complaints/{complaint.pk}/progress/', payload).status_code == 403
    User.objects.filter(pk=users['staff'].pk).update(role=User.Role.MESS)
    with pytest.raises(PermissionDenied):
        advance(users, complaint)
    assert client.get('/api/complaints/manage/').status_code == 403
    assert complaint.history.count() == 2


@pytest.mark.django_db(transaction=True)
def test_concurrent_progress_produces_one_transition(records):
    users, complaint = records
    assign(users, complaint)
    assert connection.vendor == 'postgresql'

    def attempt(actor):
        close_old_connections()
        try:
            advance(users, complaint, actor=actor)
            return 'advanced'
        except ValidationError:
            return 'stale'
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, ['director', 'staff']))
    assert sorted(results) == ['advanced', 'stale']
    complaint.refresh_from_db()
    assert complaint.status == 'In Progress'
    assert complaint.history.count() == 3
