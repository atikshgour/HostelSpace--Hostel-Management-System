# Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException, ValidationError

from .models import FeeDue, PaymentAttempt
from .payments import (
    ProviderError,
    create_order,
    fetch_order_payments,
    fetch_payment,
    valid_checkout_signature,
)


class PaymentUnavailable(APIException):
    status_code = 503
    default_code = 'payment_unavailable'
    default_detail = 'Test payment service is unavailable.'


def initiate(student, fee_id):
    with transaction.atomic():
        fee = get_object_or_404(FeeDue.objects.select_for_update(), pk=fee_id, student=student)
        if fee.status == FeeDue.Status.PAID:
            raise ValidationError({'fee': ['This fee is already paid.']})
        if fee.attempts.filter(status=PaymentAttempt.Status.PENDING).exists():
            raise ValidationError({'fee': ['Verify or cancel the pending attempt first.']})
        try:
            order_id = create_order(fee)
        except (ProviderError, ImproperlyConfigured) as exc:
            raise PaymentUnavailable() from exc
        attempt = PaymentAttempt.objects.create(
            fee=fee, provider_order_id=order_id, amount=fee.amount, currency=fee.currency,
        )
        fee.status = FeeDue.Status.PENDING
        fee.save(update_fields=['status'])
        return attempt


def verify(student, attempt_id, payment_id=None, signature=None, cancelled=False):
    with transaction.atomic():
        attempt = get_object_or_404(
            PaymentAttempt.objects.select_related('fee').select_for_update(), pk=attempt_id, fee__student=student,
        )
        fee = FeeDue.objects.select_for_update().get(pk=attempt.fee_id)
        if attempt.status != PaymentAttempt.Status.PENDING:
            return attempt
        if payment_id:
            if not valid_checkout_signature(attempt.provider_order_id, payment_id, signature):
                raise ValidationError({'payment': ['Invalid checkout signature.']})
            try:
                payment = fetch_payment(payment_id)
            except (ProviderError, ImproperlyConfigured) as exc:
                raise PaymentUnavailable() from exc
            if (payment.get('id') != payment_id or payment.get('order_id') != attempt.provider_order_id or
                    payment.get('amount') != int(attempt.amount * 100) or payment.get('currency') != attempt.currency or
                    attempt.amount != fee.amount or attempt.currency != fee.currency):
                raise ValidationError({'payment': ['Provider payment does not match this fee and order.']})
            if payment.get('status') == 'captured':
                attempt.status = PaymentAttempt.Status.SUCCEEDED
                attempt.provider_reference = payment_id
                if fee.status != FeeDue.Status.PAID:
                    fee.status = FeeDue.Status.PAID
                    fee.paid_at = timezone.now()
                    fee.save(update_fields=['status', 'paid_at'])
            elif payment.get('status') in ('failed', 'refunded'):
                attempt.status = PaymentAttempt.Status.FAILED
                attempt.provider_reference = payment_id
        else:
            try:
                payments = fetch_order_payments(attempt.provider_order_id)
            except (ProviderError, ImproperlyConfigured) as exc:
                raise PaymentUnavailable() from exc
            matching = [item for item in payments if item.get('order_id') == attempt.provider_order_id
                        and item.get('amount') == int(attempt.amount * 100)
                        and item.get('currency') == attempt.currency]
            captured = next((item for item in matching if item.get('status') == 'captured'), None)
            failed = next((item for item in matching if item.get('status') == 'failed'), None)
            if captured and attempt.amount == fee.amount and attempt.currency == fee.currency:
                attempt.status = PaymentAttempt.Status.SUCCEEDED
                attempt.provider_reference = captured['id']
                if fee.status != FeeDue.Status.PAID:
                    fee.status = FeeDue.Status.PAID
                    fee.paid_at = timezone.now()
                    fee.save(update_fields=['status', 'paid_at'])
            elif failed:
                attempt.status = PaymentAttempt.Status.FAILED
                attempt.provider_reference = failed['id']
            elif cancelled and not payments:
                attempt.status = PaymentAttempt.Status.CANCELLED
        if attempt.status != PaymentAttempt.Status.PENDING:
            attempt.resolved_at = timezone.now()
            attempt.save(update_fields=['status', 'provider_reference', 'resolved_at'])
            if fee.status != FeeDue.Status.PAID:
                fee.status = FeeDue.Status.UNPAID
                fee.save(update_fields=['status'])
        return attempt
