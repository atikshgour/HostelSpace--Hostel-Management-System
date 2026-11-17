# Owner: Atiksh Gour | US-16 | Dev sprint 3 | SRS sprint 5 | Reviewer: Anvi Srinivas (pending)
"""Razorpay TEST integration plus explicit local simulation. Never accept client amount/status as proof."""

import base64
import hashlib
import hmac
import json
import secrets
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import FeeDue, PaymentAttempt


def provider_request(path, payload=None):
    key = settings.RAZORPAY_KEY_ID
    secret = settings.RAZORPAY_KEY_SECRET
    if not key.startswith("rzp_test_") or not secret:
        raise ValidationError(
            "Configure Razorpay TEST credentials; live payments are not enabled."
        )
    auth = base64.b64encode(f"{key}:{secret}".encode()).decode()
    request = Request(
        "https://api.razorpay.com/v1/" + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:  # nosec B310
            return json.load(response)
    except (TimeoutError, URLError, HTTPError, ValueError):
        raise ValidationError(
            "Sandbox provider unavailable. No fee status was changed."
        )


def local_simulation():
    if (
        settings.PAYMENT_MODE != "simulation"
        or not settings.ALLOW_PAYMENT_SIMULATION
        or not settings.DEBUG
    ):
        raise PermissionDenied(
            "Local simulation is disabled. Use verified sandbox checkout."
        )


@transaction.atomic
def initiate(user, fee_id):
    fee = get_object_or_404(FeeDue.objects.select_for_update(), pk=fee_id, student=user)
    if fee.status == "Paid":
        raise ValidationError("This fee is already Paid.")
    mode = settings.PAYMENT_MODE
    existing = (
        PaymentAttempt.objects.filter(fee=fee, provider=mode, status="Pending")
        .order_by("-created_at")
        .first()
    )
    if existing:
        return existing
    if mode == "simulation":
        local_simulation()
        order = "sim_" + secrets.token_hex(16)
    elif mode == "razorpay":
        order_data = provider_request(
            "orders",
            {
                "amount": int(fee.amount * 100),
                "currency": fee.currency,
                "receipt": str(fee.pk),
            },
        )
        if (
            order_data.get("amount") != int(fee.amount * 100)
            or order_data.get("currency") != fee.currency
            or not str(order_data.get("id", "")).startswith("order_")
        ):
            raise ValidationError("Provider returned an invalid order.")
        order = order_data["id"]
    else:
        raise ValidationError(
            "Payment checkout is disabled. Configure the sandbox provider."
        )
    try:
        return PaymentAttempt.objects.create(
            fee=fee,
            order_id=order,
            provider=mode,
            amount=fee.amount,
            currency=fee.currency,
        )
    except IntegrityError:
        # A concurrent request may win the pending-attempt constraint after the
        # initial lookup. Return that canonical attempt instead of leaking a 500.
        existing = PaymentAttempt.objects.filter(
            fee=fee, provider=mode, status="Pending"
        ).first()
        if existing:
            return existing
        raise


@transaction.atomic
def finalize(attempt_id, user, reference, outcome, amount, currency, order):
    a = get_object_or_404(
        PaymentAttempt.objects.select_for_update(), pk=attempt_id, fee__student=user
    )
    fee = FeeDue.objects.select_for_update().get(pk=a.fee_id)
    if (
        a.order_id != order
        or a.amount != amount
        or a.currency != currency
        or a.amount != fee.amount
        or a.currency != fee.currency
    ):
        raise ValidationError("Payment does not match the server-side fee and order.")
    if a.status == "Success":
        if a.provider_reference != reference:
            raise ValidationError("Payment reference mismatch.")
        return a
    if a.status != "Pending":
        raise ValidationError("This attempt is final. Create a new attempt to retry.")
    if (
        PaymentAttempt.objects.filter(provider_reference=reference)
        .exclude(pk=a.pk)
        .exists()
    ):
        raise ValidationError("Payment reference already used.")
    if outcome == "Success" and fee.status == "Paid":
        raise ValidationError("This fee already has a successful payment.")
    a.status = outcome
    a.provider_reference = reference
    a.verified_at = timezone.now()
    a.save(update_fields=["status", "provider_reference", "verified_at"])
    if outcome == "Success":
        fee.status = "Paid"
        fee.save(update_fields=["status"])
    return a


def verify(user, attempt, payment_id, signature):
    a = get_object_or_404(PaymentAttempt, pk=attempt, fee__student=user)
    if a.provider != "razorpay":
        raise ValidationError("This is not a provider payment attempt.")
    if not payment_id.startswith("pay_") or not payment_id.replace("_", "").isalnum():
        raise ValidationError("Invalid payment reference.")
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{a.order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise ValidationError("Payment signature verification failed.")
    p = provider_request("payments/" + payment_id)
    if (
        p.get("status") != "captured"
        or p.get("order_id") != a.order_id
        or p.get("amount") != int(a.amount * 100)
        or p.get("currency") != a.currency
    ):
        raise ValidationError(
            "Payment has not been verified as captured. Fee remains unchanged."
        )
    return finalize(a.pk, user, payment_id, "Success", a.amount, a.currency, a.order_id)


def simulate(user, attempt, outcome):
    local_simulation()
    a = get_object_or_404(
        PaymentAttempt, pk=attempt, fee__student=user, provider="simulation"
    )
    reference = a.provider_reference or "sim_result_" + str(a.pk)
    return finalize(a.pk, user, reference, outcome, a.amount, a.currency, a.order_id)
