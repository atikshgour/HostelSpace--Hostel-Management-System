"""Atiksh Gour | US-13-16/20 | PDF STP pages 30-32, fixed requirement IDs."""

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from unittest import skipUnless

from django.core.exceptions import ValidationError as ModelValidationError
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.tests.test_services import DomainCase
from apps.student_services import payments
from apps.student_services.models import ComplaintTransition, FeeDue, PaymentAttempt


class STPAuditTests(DomainCase):
    def test_TC_FR07_01_prior_history_cannot_be_rewritten(self):
        row = self.post(
            "/api/complaints/", {"category": "Other", "description": "Synthetic repair"}
        ).json()
        event = ComplaintTransition.objects.get(complaint_id=row["id"])
        self.assertEqual(event.actor, self.student)
        self.assertIsNotNone(event.occurred_at)
        with self.assertRaises(ModelValidationError):
            ComplaintTransition.objects.filter(pk=event.pk).update(remarks="Changed")
        event.remarks = "Changed"
        with self.assertRaises(ModelValidationError):
            event.save()
        with self.assertRaises(ModelValidationError):
            event.delete()

    def test_TC_SEC06_01_payment_credentials_are_rejected_and_not_stored(self):
        self.assertEqual(
            self.post(
                "/api/payments/initiate/",
                {"fee": 1, "card_number": "synthetic-not-a-card"},
            ).status_code,
            403,
        )
        fields = {f.name for f in PaymentAttempt._meta.fields}
        self.assertTrue(
            fields.isdisjoint({"card_number", "cvv", "upi_pin", "password"})
        )


@skipUnless(connection.vendor == "postgresql", "STP requires PostgreSQL concurrency.")
class STPPaymentRaceTests(TransactionTestCase):
    def test_TC_NFR03_01_concurrent_success_callbacks_are_idempotent(self):
        student = User.objects.create_user(username="payment-race", role="STUDENT")
        fee = FeeDue.objects.create(
            student=student,
            title="Synthetic race",
            amount=Decimal("10.00"),
            due_date=timezone.localdate(),
        )
        attempt = PaymentAttempt.objects.create(
            fee=fee,
            order_id="order_race",
            provider="razorpay",
            amount=fee.amount,
            currency="INR",
        )
        gate = Barrier(2)

        def complete(_):
            close_old_connections()
            try:
                user = User.objects.get(pk=student.pk)
                gate.wait(timeout=10)
                return payments.finalize(
                    attempt.pk,
                    user,
                    "pay_unique",
                    "Success",
                    fee.amount,
                    "INR",
                    "order_race",
                ).pk
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(complete, range(2)))
        self.assertEqual(results, [attempt.pk, attempt.pk])
        self.assertEqual(
            PaymentAttempt.objects.filter(fee=fee, status="Success").count(), 1
        )
        fee.refresh_from_db()
        self.assertEqual(fee.status, "Paid")

    def test_TC_FR09_01_two_attempts_cannot_both_pay_one_fee(self):
        user = User.objects.create_user(username="multiple-attempts", role="STUDENT")
        fee = FeeDue.objects.create(
            student=user,
            title="Synthetic fee",
            amount=Decimal("10.00"),
            due_date=timezone.localdate(),
        )
        first = PaymentAttempt.objects.create(
            fee=fee,
            order_id="order_first",
            provider="razorpay",
            amount=fee.amount,
            currency="INR",
        )
        second = PaymentAttempt.objects.create(
            fee=fee,
            order_id="order_second",
            provider="razorpay",
            amount=fee.amount,
            currency="INR",
        )
        payments.finalize(
            first.pk, user, "pay_first", "Success", fee.amount, "INR", first.order_id
        )
        with self.assertRaises(ValidationError):
            payments.finalize(
                second.pk,
                user,
                "pay_second",
                "Success",
                fee.amount,
                "INR",
                second.order_id,
            )
        second.refresh_from_db()
        self.assertEqual(second.status, "Pending")
        with self.assertRaises(IntegrityError), transaction.atomic():
            PaymentAttempt.objects.filter(pk=second.pk).update(status="Success")


class STPMessPermissionTests(DomainCase):
    def option(self, **values):
        from apps.student_services.models import MessOption

        return MessOption.objects.create(
            name="Synthetic hall", diet="Vegetarian", **values
        )

    def test_TC_FR08_01_students_and_unrelated_staff_cannot_write(self):
        option = self.option()
        for actor in [
            self.student,
            self.stranger,
            self.warden,
            self.director,
            self.maintenance,
            self.laundry,
        ]:
            self.as_user(actor)
            self.assertEqual(
                self.post(
                    "/api/mess/select/",
                    {"option": option.pk, "student": self.student.pk},
                ).status_code,
                403,
            )
            self.assertEqual(
                self.post(
                    "/api/mess/coupons/",
                    {
                        "student": self.student.pk,
                        "code": "FORBIDDEN",
                        "valid_from": "2026-01-01",
                        "valid_to": "2026-12-31",
                    },
                ).status_code,
                403,
            )

    def test_TC_FR08_01_staff_allocation_retry_and_history(self):
        from apps.student_services.models import MessAllocation, MessChoiceEvent

        option = self.option(capacity=1)
        self.as_user(self.mess)
        body = {"option": option.pk, "student": self.student.pk}
        for _ in range(2):
            self.assertEqual(self.post("/api/mess/select/", body).status_code, 200)
        self.assertEqual(MessAllocation.objects.count(), 1)
        self.assertEqual(MessChoiceEvent.objects.count(), 1)
        event = MessChoiceEvent.objects.get()
        self.assertEqual(event.actor, self.mess)
        self.assertEqual(
            self.post(
                "/api/mess/select/", {"option": option.pk, "student": self.stranger.pk}
            ).status_code,
            400,
        )
        option.active = False
        option.save()
        self.assertEqual(self.post("/api/mess/select/", body).status_code, 400)

    def test_TC_FR08_01_only_mess_staff_publish_catalogue(self):
        body = {"name": "Published hall", "diet": "Mixed", "capacity": 10}
        for actor in [self.student, self.warden, self.director]:
            self.as_user(actor)
            self.assertEqual(self.post("/api/mess/options/", body).status_code, 403)
        self.as_user(self.mess)
        self.assertEqual(self.post("/api/mess/options/", body).status_code, 201)

    def test_TC_FR07_01_warden_cannot_read_or_assign_complaints(self):
        pk = self.post(
            "/api/complaints/", {"category": "Other", "description": "Synthetic issue"}
        ).json()["id"]
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/complaints/").status_code, 403)
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/assign/", {"assigned_to": self.maintenance.pk}
            ).status_code,
            403,
        )

    def test_TC_FR08_01_change_preserves_history_and_releases_capacity(self):
        from apps.student_services.models import MessChoiceEvent, MessOption

        first = self.option(capacity=1)
        second = MessOption.objects.create(name="Second hall", diet="Mixed", capacity=1)
        self.as_user(self.mess)
        for option, student in [
            (first, self.student),
            (second, self.student),
            (first, self.stranger),
        ]:
            self.assertEqual(
                self.post(
                    "/api/mess/select/", {"option": option.pk, "student": student.pk}
                ).status_code,
                200,
            )
        self.assertEqual(MessChoiceEvent.objects.count(), 3)
        self.assertEqual(
            MessChoiceEvent.objects.filter(student=self.student).first().old_mess,
            first.name,
        )

    def test_TC_FR08_01_enrolled_name_and_capacity_are_protected(self):
        option = self.option(capacity=1)
        self.as_user(self.mess)
        self.assertEqual(
            self.post(
                "/api/mess/select/", {"option": option.pk, "student": self.student.pk}
            ).status_code,
            200,
        )
        for data in [{"capacity": 0}, {"name": "Changed hall"}]:
            self.assertEqual(
                self.client.patch(
                    f"/api/mess/options/{option.pk}/", data, format="json"
                ).status_code,
                400,
            )
