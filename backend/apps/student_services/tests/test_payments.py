# Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.student_services.models import FeeDue, PaymentAttempt

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup():
    student = User.objects.create_user(username='synthetic-fee-student', role=User.Role.STUDENT)
    other = User.objects.create_user(username='synthetic-fee-other', role=User.Role.STUDENT)
    fee = FeeDue.objects.create(student=student, description='Synthetic hostel fee', amount=Decimal('125.50'))
    client = APIClient(enforce_csrf_checks=True)
    client.force_login(student)
    assert client.get('/api/fees/').status_code == 200
    client.credentials(HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
    return student, other, fee, client


def test_owned_fee_and_verified_capture(setup):
    student, other, fee, client = setup
    FeeDue.objects.create(student=other, description='Other fee', amount=Decimal('5.00'))
    assert len(client.get('/api/fees/').data['results']) == 1
    with patch('apps.student_services.fee_services.create_order', return_value='order_test123'), \
         patch('apps.student_services.fee_views.credentials', return_value=('rzp_test_example', 'secret')):
        response = client.post(f'/api/fees/{fee.pk}/initiate/', {}, format='json')
    assert response.status_code == 201
    attempt_id = response.data['attempt_id']
    fee.refresh_from_db()
    assert fee.status == FeeDue.Status.PENDING
    with patch('apps.student_services.fee_services.valid_checkout_signature', return_value=True), \
         patch('apps.student_services.fee_services.fetch_payment', return_value={
             'id': 'pay_test123', 'order_id': 'order_test123', 'amount': 12550,
             'currency': 'INR', 'status': 'captured',
         }):
        response = client.post(f'/api/payment-attempts/{attempt_id}/verify/',
                               {'payment_id': 'pay_test123', 'signature': 'signature'}, format='json')
    assert response.status_code == 200
    assert response.data['status'] == PaymentAttempt.Status.SUCCEEDED
    fee.refresh_from_db()
    assert fee.status == FeeDue.Status.PAID
    assert client.post(f'/api/fees/{fee.pk}/initiate/', {}, format='json').status_code == 400
    assert PaymentAttempt.objects.get(pk=attempt_id).provider_reference == 'pay_test123'
    retry = client.post(f'/api/payment-attempts/{attempt_id}/verify/',
                        {'payment_id': 'pay_test123', 'signature': 'signature'}, format='json')
    assert retry.status_code == 200
    assert retry.data['status'] == PaymentAttempt.Status.SUCCEEDED
    assert PaymentAttempt.objects.filter(fee=fee).count() == 1


def test_mismatch_stays_pending_and_cancelled_stays_unpaid(setup):
    _, _, fee, client = setup
    with patch('apps.student_services.fee_services.create_order', return_value='order_test456'), \
         patch('apps.student_services.fee_views.credentials', return_value=('rzp_test_example', 'secret')):
        attempt_id = client.post(f'/api/fees/{fee.pk}/initiate/', {}, format='json').data['attempt_id']
    with patch('apps.student_services.fee_services.valid_checkout_signature', return_value=True), \
         patch('apps.student_services.fee_services.fetch_payment', return_value={
             'id': 'pay_test456', 'order_id': 'order_test456', 'amount': 1,
             'currency': 'INR', 'status': 'captured',
         }):
        assert client.post(f'/api/payment-attempts/{attempt_id}/verify/',
                           {'payment_id': 'pay_test456', 'signature': 'signature'}, format='json').status_code == 400
    fee.refresh_from_db()
    assert fee.status == FeeDue.Status.PENDING
    with patch('apps.student_services.fee_services.fetch_order_payments', return_value=[]):
        assert client.post(f'/api/payment-attempts/{attempt_id}/verify/',
                           {'cancelled': True}, format='json').data['status'] == PaymentAttempt.Status.CANCELLED
    fee.refresh_from_db()
    assert fee.status == FeeDue.Status.UNPAID


def test_unique_provider_reference(setup):
    _, _, fee, _ = setup
    PaymentAttempt.objects.create(fee=fee, provider_order_id='order_one',
                                  provider_reference='pay_once', amount=fee.amount, currency='INR')
    with pytest.raises(IntegrityError), transaction.atomic():
        PaymentAttempt.objects.create(fee=fee, provider_order_id='order_two',
                                      provider_reference='pay_once', amount=fee.amount, currency='INR')
