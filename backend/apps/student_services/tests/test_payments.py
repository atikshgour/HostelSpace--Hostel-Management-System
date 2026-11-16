# Owner: Atiksh Gour | US-16,US-24 | Dev sprint 3; 5–6 | SRS sprint 5; 6 | Reviewer: Anvi Srinivas (pending)
import hashlib
import hmac
from unittest.mock import patch

from django.test import override_settings
from django.utils import timezone

from apps.accounts.tests.test_services import DomainCase
from apps.student_services.models import FeeDue, PaymentAttempt


@override_settings(DEBUG=True, PAYMENT_MODE="simulation", ALLOW_PAYMENT_SIMULATION=True)
class PaymentTests(DomainCase):
    def setUp(self):
        super().setUp()
        self.fee = FeeDue.objects.create(
            student=self.student,
            title="Test fee",
            amount="100.00",
            currency="INR",
            due_date=timezone.localdate(),
        )

    def start(self):
        return self.post("/api/payments/initiate/", {"fee": self.fee.pk})

    def test_simulation_explicit_label_and_server_amount(self):
        r = self.start()
        self.assertEqual(r.status_code, 201)
        self.assertIn("SIMULATION", r.json()["simulation_label"])
        self.assertEqual(r.json()["amount"], "100.00")

    def test_caller_cannot_supply_amount(self):
        self.assertEqual(
            self.post(
                "/api/payments/initiate/", {"fee": self.fee.pk, "amount": "1.00"}
            ).status_code,
            403,
        )

    def test_cannot_pay_others_fee(self):
        self.as_user(self.stranger)
        self.assertEqual(self.start().status_code, 404)

    @override_settings(ALLOW_PAYMENT_SIMULATION=False)
    def test_simulation_disabled_without_opt_in(self):
        self.assertEqual(self.start().status_code, 403)

    @override_settings(DEBUG=False)
    def test_simulation_not_allowed_outside_local(self):
        self.assertEqual(self.start().status_code, 403)

    def test_failure_and_cancellation_keep_fee_unpaid(self):
        for outcome in ["Failed", "Cancelled"]:
            a = self.start().json()
            r = self.post(
                "/api/payments/simulate/", {"attempt": a["id"], "outcome": outcome}
            )
            self.assertEqual(r.status_code, 200)
            self.fee.refresh_from_db()
            self.assertEqual(self.fee.status, "Unpaid")
        self.assertEqual(PaymentAttempt.objects.count(), 2)

    def test_success_is_idempotent_and_marks_paid(self):
        a = self.start().json()
        body = {"attempt": a["id"], "outcome": "Success"}
        for _ in range(2):
            self.assertEqual(
                self.post("/api/payments/simulate/", body).status_code, 200
            )
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.status, "Paid")
        self.assertEqual(PaymentAttempt.objects.count(), 1)
        self.assertEqual(self.start().status_code, 400)

    def test_failed_attempt_cannot_silently_become_success(self):
        a = self.start().json()
        self.post("/api/payments/simulate/", {"attempt": a["id"], "outcome": "Failed"})
        self.assertEqual(
            self.post(
                "/api/payments/simulate/", {"attempt": a["id"], "outcome": "Success"}
            ).status_code,
            400,
        )

    def test_unverified_attempt_stays_pending(self):
        a = self.start().json()
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.status, "Unpaid")
        self.assertEqual(PaymentAttempt.objects.get(pk=a["id"]).status, "Pending")

    @override_settings(
        PAYMENT_MODE="razorpay",
        RAZORPAY_KEY_ID="rzp_test_unit",
        RAZORPAY_KEY_SECRET="unit-only-secret",
    )
    @patch("apps.student_services.payments.provider_request")
    def test_provider_success_requires_valid_signature_and_capture(self, provider):
        provider.return_value = {"id": "order_test", "amount": 10000, "currency": "INR"}
        a = self.start().json()
        body = {"attempt": a["id"], "payment_id": "pay_test", "signature": "bad"}
        self.assertEqual(self.post("/api/payments/verify/", body).status_code, 400)
        body["signature"] = hmac.new(
            b"unit-only-secret", b"order_test|pay_test", hashlib.sha256
        ).hexdigest()
        provider.return_value = {
            "status": "captured",
            "amount": 10000,
            "currency": "INR",
            "order_id": "order_test",
        }
        self.assertEqual(self.post("/api/payments/verify/", body).status_code, 200)
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.status, "Paid")

    @override_settings(
        PAYMENT_MODE="razorpay",
        RAZORPAY_KEY_ID="rzp_test_unit",
        RAZORPAY_KEY_SECRET="unit-only-secret",
    )
    @patch("apps.student_services.payments.provider_request")
    def test_provider_mismatched_amount_cannot_mark_paid(self, provider):
        provider.return_value = {"id": "order_test", "amount": 10000, "currency": "INR"}
        a = self.start().json()
        signature = hmac.new(
            b"unit-only-secret", b"order_test|pay_test", hashlib.sha256
        ).hexdigest()
        provider.return_value = {
            "status": "captured",
            "amount": 1,
            "currency": "INR",
            "order_id": "order_test",
        }
        self.assertEqual(
            self.post(
                "/api/payments/verify/",
                {"attempt": a["id"], "payment_id": "pay_test", "signature": signature},
            ).status_code,
            400,
        )
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.status, "Unpaid")

    def test_payment_history_is_owner_scoped(self):
        self.start()
        self.as_user(self.stranger)
        self.assertEqual(
            self.client.get("/api/payments/attempts/").json()["results"], []
        )
