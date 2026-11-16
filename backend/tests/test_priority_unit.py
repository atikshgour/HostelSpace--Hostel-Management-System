"""Team test review | US-18/22 | Isolated validators and boundary decisions."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch
from urllib.error import URLError

import pytest
from django.test import override_settings
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.permissions import require
from apps.leave_attendance.location import check_sample, distance_m
from apps.leave_attendance.serializers import LeaveInput
from apps.student_services.payments import provider_request

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "change,expected",
    [
        ({}, (True, "WITHIN_POLICY")),
        ({"latitude": 13.0}, (False, "OUTSIDE_RADIUS")),
        ({"accuracy_m": 51}, (False, "LOW_ACCURACY")),
        ({"sampled_at_offset": -61}, (False, "STALE_SAMPLE")),
        ({"sampled_at_offset": 6}, (False, "STALE_SAMPLE")),
    ],
)
def test_attendance_boundary_decisions(change, expected):
    now = datetime(2026, 11, 16, 12, tzinfo=timezone.utc)
    session = SimpleNamespace(
        opens_at=now - timedelta(minutes=1),
        closes_at=now + timedelta(minutes=1),
        centre_latitude=12.0,
        centre_longitude=77.0,
        radius_m=100,
        max_accuracy_m=50,
        max_sample_age_seconds=60,
    )
    sample = {"latitude": 12.0, "longitude": 77.0, "accuracy_m": 5, "sampled_at": now}
    change = dict(change)
    if "sampled_at_offset" in change:
        sample["sampled_at"] = now + timedelta(seconds=change.pop("sampled_at_offset"))
    sample.update(change)
    assert check_sample(session, sample, now) == expected


def test_haversine_distance_identity_and_scale():
    assert distance_m(12, 77, 12, 77) == 0
    assert distance_m(0, 0, 0, 1) == pytest.approx(111195, abs=5)


@pytest.mark.parametrize(
    "body,valid",
    [
        (
            {
                "start_date": "2026-11-16",
                "end_date": "2026-11-17",
                "reason": "Synthetic leave",
            },
            True,
        ),
        ({}, False),
        (
            {
                "start_date": "2026-11-17",
                "end_date": "2026-11-16",
                "reason": "Synthetic leave",
            },
            False,
        ),
        ({"start_date": "2026-11-16", "end_date": "2026-11-17", "reason": " "}, False),
    ],
)
def test_leave_input_validation(body, valid):
    assert LeaveInput(data=body).is_valid() is valid


@pytest.mark.security
@pytest.mark.parametrize(
    "role,active,authenticated,allowed",
    [
        ("DIRECTOR", True, True, True),
        ("STUDENT", True, True, False),
        ("DIRECTOR", False, True, False),
        ("DIRECTOR", True, False, False),
    ],
)
def test_active_role_permission(role, active, authenticated, allowed):
    user = SimpleNamespace(role=role, is_active=active, is_authenticated=authenticated)
    if allowed:
        require(user, "DIRECTOR")
    else:
        with pytest.raises(PermissionDenied):
            require(user, "DIRECTOR")


@pytest.mark.reliability
@override_settings(
    RAZORPAY_KEY_ID="rzp_test_synthetic", RAZORPAY_KEY_SECRET="synthetic-test-value"
)
def test_wrapped_provider_timeout_is_validation_error():
    with patch(
        "apps.student_services.payments.urlopen",
        side_effect=URLError(TimeoutError("Synthetic timeout")),
    ):
        with pytest.raises(ValidationError, match="unavailable"):
            provider_request("orders", {"amount": 100, "currency": "INR"})


@pytest.mark.reliability
@override_settings(
    RAZORPAY_KEY_ID="rzp_test_synthetic", RAZORPAY_KEY_SECRET="synthetic-test-value"
)
def test_direct_socket_timeout_is_validation_error():
    # urlopen can also raise TimeoutError directly; no live provider is contacted.
    with patch(
        "apps.student_services.payments.urlopen",
        side_effect=TimeoutError("Synthetic direct socket timeout"),
    ):
        with pytest.raises(ValidationError, match="unavailable"):
            provider_request("orders", {"amount": 100, "currency": "INR"})
