"""Team test review | US-18/22/23 | Fourteen requested priority workflows.

Synthetic fixtures only. Provider I/O is mocked. Tests expose gaps without
changing production behavior or weakening existing assertions.
"""

import secrets
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from urllib.error import URLError

import pytest
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.tests.test_services import DomainCase
from apps.leave_attendance.models import Attendance, Deviation, LeaveRequest
from apps.student_services.models import Complaint, FeeDue, PaymentAttempt

pytestmark = [pytest.mark.integration, pytest.mark.system]


@override_settings(DEBUG=True, PAYMENT_MODE="simulation", ALLOW_PAYMENT_SIMULATION=True)
class PriorityAcceptanceTests(DomainCase):
    def login_client(self):
        cache.clear()
        password = secrets.token_urlsafe(24)
        self.student.set_password(password)
        self.student.save(update_fields=["password"])
        client = APIClient(enforce_csrf_checks=True)
        token = client.get("/api/auth/csrf/").json()["csrfToken"]
        return client, token, password

    def fee(self, title="Priority synthetic fee"):
        return FeeDue.objects.create(
            student=self.student,
            title=title,
            amount=Decimal("100.00"),
            currency="INR",
            due_date=timezone.localdate(),
        )

    def initiate(self, fee):
        return self.post("/api/payments/initiate/", {"fee": fee.pk})

    def test_P01_valid_login(self):
        client, token, password = self.login_client()
        response = client.post(
            "/api/auth/login/",
            {"username": self.student.username, "password": password},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(client.get("/api/auth/me/").json()["id"], self.student.pk)

    @pytest.mark.security
    def test_P02_invalid_login(self):
        client, token, _ = self.login_client()
        response = client.post(
            "/api/auth/login/",
            {"username": self.student.username, "password": "synthetic-wrong-value"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], "invalid_credentials")
        self.assertEqual(client.get("/api/auth/me/").status_code, 403)

    @pytest.mark.security
    def test_P03_student_denied_staff_and_admin_actions(self):
        for endpoint in (
            "/api/director/users/",
            "/api/director/settings/",
            "/api/director/summary/",
        ):
            self.assertEqual(self.client.get(endpoint).status_code, 403)
        self.assertEqual(self.post("/api/attendance/sessions/", {}).status_code, 403)
        self.assertEqual(self.post("/api/deviations/", {}).status_code, 403)

    def test_P04_valid_leave(self):
        response = self.post("/api/leaves/", self.leave_data)
        self.assertEqual(response.status_code, 201)
        row = LeaveRequest.objects.get(pk=response.json()["id"])
        self.assertEqual(row.student, self.student)
        self.assertEqual(row.assigned_warden, self.warden)
        self.assertEqual(row.status, "Pending")
        self.assertEqual(row.transitions.get().actor, self.student)

    def test_P05_invalid_leave(self):
        variants = [
            {},
            {**self.leave_data, "reason": " "},
            {
                **self.leave_data,
                "end_date": self.leave_data["start_date"] - timedelta(days=1),
            },
        ]
        for body in variants:
            self.assertEqual(self.post("/api/leaves/", body).status_code, 400)
        self.assertEqual(LeaveRequest.objects.count(), 0)

    def test_P06_warden_approves_and_rejects(self):
        for decision in ("Approved", "Rejected"):
            self.as_user(self.student)
            row = self.post("/api/leaves/", self.leave_data).json()
            self.as_user(self.warden)
            response = self.post(
                f"/api/leaves/{row['id']}/decision/",
                {"decision": decision, "remarks": "Synthetic review"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], decision)
            self.assertEqual(len(response.json()["transitions"]), 2)

    def test_P07_valid_attendance(self):
        response = self.post(
            "/api/attendance/submit/", {"session": str(self.session.pk), **self.sample}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["result"], "Accepted")
        self.assertNotIn("latitude", response.json())

    def test_P08_outside_boundary_rejected(self):
        response = self.post(
            "/api/attendance/submit/",
            {"session": str(self.session.pk), **self.sample, "latitude": 13.0},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["result"], "Rejected")
        self.assertEqual(response.json()["reason_code"], "OUTSIDE_RADIUS")
        self.assertEqual(Attendance.objects.filter(result="Accepted").count(), 0)

    @pytest.mark.reliability
    def test_P09_repeated_attendance_prevented(self):
        body = {"session": str(self.session.pk), **self.sample}
        self.assertEqual(self.post("/api/attendance/submit/", body).status_code, 201)
        self.assertEqual(self.post("/api/attendance/submit/", body).status_code, 409)
        self.assertEqual(Attendance.objects.count(), 1)

    @pytest.mark.security
    def test_P10_complaint_creation_and_ownership(self):
        row = self.post(
            "/api/complaints/",
            {"category": "Other", "description": "Synthetic own complaint"},
        ).json()
        self.as_user(self.stranger)
        other = self.post(
            "/api/complaints/",
            {"category": "Other", "description": "Synthetic other complaint"},
        ).json()
        self.as_user(self.student)
        ids = [
            item["id"] for item in self.client.get("/api/complaints/").json()["results"]
        ]
        self.assertEqual(ids, [row["id"]])
        self.assertEqual(
            self.client.get(f"/api/complaints/{other['id']}/").status_code, 404
        )

    @pytest.mark.security
    def test_P11_unauthorized_complaint_update(self):
        row = self.post(
            "/api/complaints/",
            {"category": "Other", "description": "Synthetic protected complaint"},
        ).json()
        self.as_user(self.stranger)
        response = self.post(
            f"/api/complaints/{row['id']}/progress/",
            {"status": "Resolved", "remarks": "Forbidden"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Complaint.objects.get(pk=row["id"]).status, "Open")

    @pytest.mark.reliability
    def test_P12_payment_success_failure_timeout_retry(self):
        fee = self.fee()
        failed = self.initiate(fee).json()
        self.assertEqual(
            self.post(
                "/api/payments/simulate/",
                {"attempt": failed["id"], "outcome": "Failed"},
            ).status_code,
            200,
        )
        fee.refresh_from_db()
        self.assertEqual(fee.status, "Unpaid")
        # Provider timeout is simulated before any network call or order exists.
        with override_settings(
            PAYMENT_MODE="razorpay",
            RAZORPAY_KEY_ID="rzp_test_synthetic",
            RAZORPAY_KEY_SECRET="synthetic-test-value",
        ):
            with patch(
                "apps.student_services.payments.urlopen",
                side_effect=URLError(TimeoutError("Synthetic timeout")),
            ):
                self.assertEqual(self.initiate(fee).status_code, 400)
        self.assertEqual(PaymentAttempt.objects.filter(fee=fee).count(), 1)
        retry = self.initiate(fee).json()
        self.assertNotEqual(retry["id"], failed["id"])
        self.assertEqual(
            self.post(
                "/api/payments/simulate/",
                {"attempt": retry["id"], "outcome": "Success"},
            ).status_code,
            200,
        )
        fee.refresh_from_db()
        self.assertEqual(fee.status, "Paid")
        self.assertEqual(PaymentAttempt.objects.get(pk=failed["id"]).status, "Failed")

    @pytest.mark.reliability
    def test_P13_duplicate_payment_callbacks_and_submissions(self):
        fee = self.fee()
        first = self.initiate(fee).json()
        repeated = self.initiate(fee).json()
        pending_count = PaymentAttempt.objects.filter(fee=fee).count()
        body = {"attempt": first["id"], "outcome": "Success"}
        for _ in range(2):
            self.assertEqual(
                self.post("/api/payments/simulate/", body).status_code, 200
            )
        self.assertEqual(
            PaymentAttempt.objects.filter(fee=fee, status="Success").count(), 1
        )
        self.assertEqual(self.initiate(fee).status_code, 400)
        # Identical pending initiation currently has no retry correlation key.
        self.assertEqual(
            pending_count,
            1,
            "Repeated pending initiation created separate PaymentAttempt rows",
        )
        self.assertEqual(first["id"], repeated["id"])

    @pytest.mark.reliability
    def test_P14_deviation_total_and_duplicate_prevention(self):
        self.as_user(self.warden)
        body = {
            "student": str(self.student.pk),
            "rule": str(self.rule.pk),
            "remarks": "Synthetic identical submission",
        }
        first = self.post("/api/deviations/", body)
        self.assertEqual(first.status_code, 201)
        total = self.client.get(
            f"/api/deviations/total/?student={self.student.pk}"
        ).json()
        self.assertEqual(Decimal(total["active_total"]), self.rule.weightage)
        self.post("/api/deviations/", body)
        total = self.client.get(
            f"/api/deviations/total/?student={self.student.pk}"
        ).json()
        self.assertEqual(
            Deviation.objects.filter(student=self.student).count(),
            1,
            "Identical repeated deviation submission created a second record",
        )
        self.assertEqual(Decimal(total["active_total"]), self.rule.weightage)
