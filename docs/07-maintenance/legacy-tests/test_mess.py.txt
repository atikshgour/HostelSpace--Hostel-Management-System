# Owner: Atiksh Gour | US-15 / TC-FR08-01 / SEC-03 | Sprint 5 | Reviewer: Anvi Srinivas
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.utils.timezone import localdate as real_localdate
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.student_services.mess_services import (
    create_allocation,
    create_coupon,
    update_allocation,
)
from apps.student_services.models import Coupon, MessAllocation

pytestmark = pytest.mark.django_db
TODAY = date(2026, 10, 29)
BASE = '/api/mess/'


@pytest.fixture
def users():
    return {name: User.objects.create_user(username=f'synthetic-{name}', role=role)
            for name, role in [('staff', User.Role.MESS), ('staff2', User.Role.MESS),
                               ('student', User.Role.STUDENT), ('other', User.Role.STUDENT)]}


@pytest.fixture(autouse=True)
def fixed_today():
    with patch('apps.student_services.mess_views.timezone.localdate', return_value=TODAY):
        yield


def payload(users, **extra):
    return {'student': users['student'].pk, 'mess_name': 'Synthetic mess',
            'valid_from': '2026-10-29', 'valid_until': '2026-10-29', **extra}


def session(user, staff=False):
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(user)
    response = client.get(BASE + ('allocations/' if staff else ''))
    assert response.status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
    return client


@pytest.fixture
def allocation(users):
    return create_allocation(actor=users['staff'], data=payload(users))


def coupon_payload(allocation_record, **extra):
    return {'allocation': allocation_record.pk, 'code': 'SYNTHETIC-COUPON',
            'valid_from': '2026-10-29', 'valid_until': '2026-10-29', **extra}


def error(response, status, code='validation_error'):
    assert response.status_code == status
    assert set(response.data) == {'code', 'message', 'fields'}
    assert response.data['code'] == code
    assert 'no-store' in response['Cache-Control']


def test_staff_creates_updates_and_student_refreshes_personal_data(users):
    staff = session(users['staff'], True)
    response = staff.post(BASE + 'allocations/', payload(users, mess_name='  Synthetic mess  '), format='json')
    assert response.status_code == 201
    allocation = MessAllocation.objects.get(pk=response.data['id'])
    assert allocation.mess_name == 'Synthetic mess'
    assert allocation.updated_by_id == users['staff'].pk
    assert allocation.updated_at is not None
    response = staff.post(BASE + 'coupons/', coupon_payload(allocation, code=' SYNTHETIC-COUPON '), format='json')
    assert response.status_code == 201
    coupon = Coupon.objects.get(pk=response.data['id'])
    assert coupon.code == 'SYNTHETIC-COUPON'
    student = session(users['student'])
    data = student.get(BASE).data
    assert data['as_of'] == '2026-10-29'
    assert data['timezone'] == 'Asia/Kolkata'
    assert data['allocation']['id'] == allocation.pk
    assert [item['id'] for item in data['coupons']] == [coupon.pk]
    response = staff.patch(f'{BASE}allocations/{allocation.pk}/', {
        'mess_name': 'Synthetic updated mess', 'expected_version': 1,
    }, format='json')
    assert response.status_code == 200
    assert response.data['version'] == 2
    response = staff.patch(f'{BASE}coupons/{coupon.pk}/', {
        'is_active': False, 'expected_version': 1,
    }, format='json')
    assert response.status_code == 200
    assert session(users['student']).get(BASE).data['coupons'] == []
    assert student.get(BASE).data['allocation']['mess_name'] == 'Synthetic updated mess'
    assert session(users['other']).get(BASE).data['allocation'] is None
    assert session(users['other']).get(BASE).data['coupons'] == []


@pytest.mark.parametrize('active,start,end,visible', [
    (True, 0, 0, True), (True, -1, 0, True), (True, 0, 1, True),
    (True, -2, -1, False), (True, 1, 2, False), (False, -1, 1, False),
])
def test_allocation_current_active_boundaries(users, active, start, end, visible):
    allocation = MessAllocation.objects.create(student=users['student'], updated_by=users['staff'],
        mess_name='Synthetic', is_active=active, valid_from=TODAY + timedelta(days=start),
        valid_until=TODAY + timedelta(days=end))
    Coupon.objects.create(allocation=allocation, updated_by=users['staff'], code='SYNTHETIC',
                          valid_from=TODAY, valid_until=TODAY)
    data = session(users['student']).get(BASE).data
    assert bool(data['allocation']) is visible
    assert bool(data['coupons']) is visible


@pytest.mark.parametrize('active,start,end,visible', [
    (True, 0, 0, True), (True, -1, 0, True), (True, 0, 1, True),
    (True, -2, -1, False), (True, 1, 2, False), (False, -1, 1, False),
])
def test_coupon_current_active_boundaries(users, allocation, active, start, end, visible):
    Coupon.objects.create(allocation=allocation, updated_by=users['staff'], code='SYNTHETIC',
        is_active=active, valid_from=TODAY + timedelta(days=start), valid_until=TODAY + timedelta(days=end))
    assert bool(session(users['student']).get(BASE).data['coupons']) is visible


def test_india_midnight_changes_validity(users, allocation):
    with patch('apps.student_services.mess_views.timezone.localdate', side_effect=real_localdate):
        with patch('django.utils.timezone.now', return_value=datetime(2026, 10, 28, 18, 29, tzinfo=timezone.utc)):
            assert session(users['student']).get(BASE).data['allocation'] is None
        with patch('django.utils.timezone.now', return_value=datetime(2026, 10, 28, 18, 30, tzinfo=timezone.utc)):
            assert session(users['student']).get(BASE).data['allocation'] is not None


@pytest.mark.parametrize('role', [User.Role.STUDENT, User.Role.WARDEN, User.Role.CHIEF_WARDEN,
                                  User.Role.HOSTEL_DIRECTOR, User.Role.MAINTENANCE, User.Role.LAUNDRY])
def test_non_mess_roles_cannot_read_management_or_write(users, allocation, role):
    user = User.objects.create_user(username='synthetic-denied', role=role, is_superuser=True)
    client = APIClient()
    client.force_login(user)
    for path in ['students/', 'allocations/', 'coupons/', f'allocations/{allocation.pk}/', 'coupons/99999/']:
        error(client.get(BASE + path), 403, 'permission_denied')
        error(client.post(BASE + path, {}), 403, 'permission_denied')
        error(client.patch(BASE + path, {}), 403, 'permission_denied')


def test_student_filters_cannot_select_another_identity(users, allocation):
    response = session(users['other']).get(BASE, {'student': users['student'].pk, 'allocation': allocation.pk})
    assert response.data['allocation'] is None
    assert response.data['coupons'] == []
    error(session(users['student']).post(BASE, {}), 405, 'method_not_allowed')
    error(session(users['staff'], True).get(BASE), 403, 'permission_denied')


@pytest.mark.parametrize('extra', [
    {'mess_name': ''}, {'mess_name': '  '}, {'mess_name': 'x' * 101}, {'mess_name': 123},
    {'valid_until': '2026-10-28'}, {'valid_from': '2026-02-30'}, {'valid_from': None},
    {'student': True}, {'student': 99999}, {'is_active': 'true'},
    {'updated_by': 1}, {'version': 99}, {'coupons': []},
])
def test_invalid_allocation_does_not_write(users, extra):
    response = session(users['staff'], True).post(BASE + 'allocations/', payload(users, **extra), format='json')
    error(response, 400)
    assert not MessAllocation.objects.exists()


@pytest.mark.parametrize('extra', [
    {'code': ''}, {'code': ' '}, {'code': 'x' * 81}, {'code': 123}, {'code': None},
    {'valid_until': '2026-10-28'}, {'valid_from': 'invalid'}, {'allocation': 99999},
    {'student': 1}, {'updated_at': 'forged'}, {'is_active': 1},
])
def test_invalid_coupon_does_not_write(users, allocation, extra):
    response = session(users['staff'], True).post(BASE + 'coupons/', coupon_payload(allocation, **extra), format='json')
    error(response, 400)
    assert not Coupon.objects.exists()


def test_missing_fields_and_inactive_student(users):
    staff = session(users['staff'], True)
    error(staff.post(BASE + 'allocations/', {}, format='json'), 400)
    error(staff.post(BASE + 'coupons/', {}, format='json'), 400)
    User.objects.filter(pk=users['student'].pk).update(is_active=False)
    error(staff.post(BASE + 'allocations/', payload(users), format='json'), 400)
    assert not MessAllocation.objects.exists()


def test_partial_updates_validate_merged_dates_and_identity(users, allocation):
    staff = session(users['staff'], True)
    url = f'{BASE}allocations/{allocation.pk}/'
    for values in [{'valid_until': '2026-10-28'}, {'valid_from': '2026-10-30'},
                   {'student': users['other'].pk}, {'mess_name': ''}, {'is_active': None}]:
        error(staff.patch(url, {**values, 'expected_version': 1}, format='json'), 400)
    error(staff.patch(url, {'mess_name': 'Synthetic'}, format='json'), 400)
    error(staff.patch(url, {'expected_version': 1}, format='json'), 400)
    response = staff.patch(url, {'is_active': False, 'expected_version': 1}, format='json')
    assert response.status_code == 200
    error(staff.patch(url, {'mess_name': 'Stale', 'expected_version': 1}, format='json'), 400)
    assert session(users['student']).get(BASE).data['allocation'] is None
    allocation.refresh_from_db()
    assert allocation.mess_name == 'Synthetic mess'
    assert allocation.version == 2


def test_coupon_update_identity_dates_code_and_stale_version(users, allocation):
    staff = session(users['staff'], True)
    coupon = create_coupon(actor=users['staff'], data=coupon_payload(allocation))
    url = f'{BASE}coupons/{coupon.pk}/'
    for values in [{'valid_until': '2026-10-28'}, {'code': ''}, {'allocation': allocation.pk},
                   {'code': 13}]:
        error(staff.patch(url, {**values, 'expected_version': 1}, format='json'), 400)
    assert staff.patch(url, {'code': 'SYNTHETIC-NEW', 'expected_version': 1}, format='json').status_code == 200
    error(staff.patch(url, {'is_active': False, 'expected_version': 1}, format='json'), 400)
    assert session(users['student']).get(BASE).data['coupons'][0]['code'] == 'SYNTHETIC-NEW'


def test_duplicates_return_validation_and_missing_records_return_404(users, allocation):
    staff = session(users['staff'], True)
    error(staff.post(BASE + 'allocations/', payload(users), format='json'), 400)
    data = coupon_payload(allocation)
    assert staff.post(BASE + 'coupons/', data, format='json').status_code == 201
    error(staff.post(BASE + 'coupons/', data, format='json'), 400)
    for path in ['allocations/99999/', 'coupons/99999/']:
        error(staff.get(BASE + path), 404, 'not_found')
        error(staff.patch(BASE + path, {}, format='json'), 404, 'not_found')
    assert Coupon.objects.count() == 1


def test_sessions_csrf_changed_roles_and_no_deletion(users, allocation):
    error(APIClient().get(BASE), 401, 'not_authenticated')
    error(APIClient().get(BASE + 'allocations/'), 401, 'not_authenticated')
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(users['staff'])
    error(client.post(BASE + 'coupons/', coupon_payload(allocation), format='json'), 403, 'permission_denied')
    staff = session(users['staff'], True)
    error(staff.delete(f'{BASE}allocations/{allocation.pk}/'), 405, 'method_not_allowed')
    User.objects.filter(pk=users['staff'].pk).update(role=User.Role.STUDENT)
    with pytest.raises(PermissionDenied):
        create_coupon(actor=users['staff'], data=coupon_payload(allocation))
    error(staff.get(BASE + 'allocations/'), 403, 'permission_denied')
    User.objects.filter(pk=users['staff'].pk).update(is_active=False)
    error(staff.get(BASE), 401, 'not_authenticated')


def test_database_constraints(users, allocation):
    with pytest.raises(IntegrityError), transaction.atomic():
        MessAllocation.objects.create(student=users['student'], updated_by=users['staff'],
            mess_name='Duplicate', valid_from=TODAY, valid_until=TODAY)
    for model, values in [(MessAllocation, {'student': users['other'], 'mess_name': ' '}),
                          (Coupon, {'allocation': allocation, 'code': ' '})]:
        with pytest.raises(IntegrityError), transaction.atomic():
            model.objects.create(**values, updated_by=users['staff'], valid_from=TODAY, valid_until=TODAY)
        values['mess_name' if model is MessAllocation else 'code'] = 'Synthetic'
        with pytest.raises(IntegrityError), transaction.atomic():
            model.objects.create(**values, updated_by=users['staff'], valid_from=TODAY, valid_until=TODAY - timedelta(days=1))
    Coupon.objects.create(allocation=allocation, code='SYNTHETIC', updated_by=users['staff'],
                          valid_from=TODAY, valid_until=TODAY)
    with pytest.raises(IntegrityError), transaction.atomic():
        Coupon.objects.create(allocation=allocation, code='SYNTHETIC', updated_by=users['staff'],
                              valid_from=TODAY, valid_until=TODAY)


def test_coupon_code_conflict_does_not_overwrite_record(users, allocation):
    first = create_coupon(actor=users['staff'], data=coupon_payload(allocation))
    second = create_coupon(actor=users['staff'], data=coupon_payload(allocation, code='SYNTHETIC-SECOND'))
    response = session(users['staff'], True).patch(f'{BASE}coupons/{second.pk}/', {
        'code': first.code, 'expected_version': 1,
    }, format='json')
    error(response, 400)
    second.refresh_from_db()
    assert second.code == 'SYNTHETIC-SECOND'
    assert second.version == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_coupon_creation_has_one_winner(users, allocation):
    def create(actor):
        close_old_connections()
        try:
            create_coupon(actor=users[actor], data=coupon_payload(allocation))
            return 'created'
        except ValidationError:
            return 'duplicate'
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(create, ['staff', 'staff2'])) == ['created', 'duplicate']
    assert Coupon.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_allocation_creation_has_one_winner(users):
    assert connection.vendor == 'postgresql'

    def create(actor):
        close_old_connections()
        try:
            create_allocation(actor=users[actor], data=payload(users))
            return 'created'
        except ValidationError:
            return 'duplicate'
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(create, ['staff', 'staff2'])) == ['created', 'duplicate']
    assert MessAllocation.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_updates_reject_stale_write(users, allocation):
    def update(actor):
        close_old_connections()
        try:
            update_allocation(actor=users[actor], pk=allocation.pk,
                              data={'expected_version': 1, 'mess_name': f'Synthetic {actor}'})
            return 'updated'
        except ValidationError:
            return 'stale'
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(update, ['staff', 'staff2'])) == ['stale', 'updated']
    allocation.refresh_from_db()
    assert allocation.version == 2
