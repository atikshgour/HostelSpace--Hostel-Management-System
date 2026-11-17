"""US-22/23 | Team regression: scope, staff edits, setup and provider failures.

Use real PostgreSQL fixtures; mock only external I/O and environment boundaries.
"""

import hashlib
import hmac
import io
import json
import os
import runpy
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.test import override_settings
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import StudentProfile, User
from apps.accounts.services import check_assignments, identity
from apps.accounts.tests.test_services import DomainCase
from apps.director_dashboard.services import save_user
from apps.leave_attendance import access, permissions, services
from apps.leave_attendance.models import Attendance, AttendanceSession, LeaveRequest
from apps.student_services import payments
from apps.student_services.models import FeeDue, MessOption


class StaffBranches(DomainCase):
    def test_director_rejects_unsafe_account_transitions(self):
        for obj, data in [
            (None, {}),
            (self.student, {"role": "MESS_STAFF"}),
            (self.mess, {"role": "STUDENT"}),
            (self.warden, {"role": "MESS_STAFF"}),
            (self.chief, {"role": "MESS_STAFF"}),
            (self.director, {"is_active": False}),
            (self.warden, {"is_active": False}),
            (self.chief, {"is_active": False}),
        ]:
            with self.subTest(data=data, user=getattr(obj, "username", None)):
                with self.assertRaises(ValidationError):
                    save_user(self.director, data, obj)
        self.assertTrue(User.objects.get(pk=self.director.pk).is_active)

    def test_director_creates_converts_and_rejects_conflicting_users(self):
        password = "Synthetic-unique-78214!"
        with self.assertRaises(ValidationError):
            save_user(
                self.director,
                {"username": "new", "password": password, "role": "STUDENT"},
            )
        with self.assertRaises(ValidationError):
            save_user(
                self.director,
                {"username": "new", "password": "123", "role": "MESS_STAFF"},
            )
        with self.assertRaises(ValidationError):
            save_user(
                self.director,
                {
                    "username": self.mess.username,
                    "password": password,
                    "role": "MESS_STAFF",
                },
            )
        created = save_user(
            self.director,
            {"username": "extra", "password": password, "role": "MESS_STAFF"},
        )
        save_user(self.director, {"role": "CONTENT_STAFF", "is_active": False}, created)
        created.refresh_from_db()
        self.assertEqual((created.role, created.is_active), ("CONTENT_STAFF", False))
        self.assertTrue(created.check_password(password))
        self.as_user(self.director)
        response = self.client.patch(
            f"/api/director/users/{created.pk}/", {"is_active": True}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_assignment_validation_and_identity_without_warden(self):
        with self.assertRaises(ValidationError):
            check_assignments("STUDENT", None, self.mess)
        profile = self.student.student_profile
        profile.assigned_warden = None
        profile.save()
        self.assertEqual(
            identity(self.student)["profile"]["warden_name"], "Not assigned"
        )

    def test_choice_directories_enforce_roles_and_assignments(self):
        for actor, requested, expected in [
            (self.director, "nonsense", 200),
            (self.laundry, "WARDEN", 403),
            (self.warden, "STUDENT", 200),
            (self.warden, "WARDEN", 200),
            (self.warden, "LAUNDRY_STAFF", 200),
        ]:
            self.as_user(actor)
            r = self.client.get("/api/choices/users/", {"role": requested})
            self.assertEqual(r.status_code, expected)
            if requested in ("nonsense", "WARDEN") and expected == 200:
                self.assertEqual(r.json()["results"], [])
        # Older account directory is tested directly; it is not a registered API.
        from rest_framework.test import APIRequestFactory, force_authenticate

        from apps.accounts.views import UserChoices

        factory = APIRequestFactory()
        for actor, role, status in [
            (self.warden, "STUDENT", 200),
            (self.director, "MAINTENANCE_STAFF", 200),
            (self.mess, "MAINTENANCE_STAFF", 403),
            (self.director, "DIRECTOR", 400),
        ]:
            request = factory.get("/", {"role": role})
            force_authenticate(request, actor)
            r = UserChoices.as_view()(request)
            self.assertEqual(r.status_code, status)

    def test_staff_content_edits_and_empty_study_fallback(self):
        self.assertEqual(self.client.get("/api/study-room/").json()["status"], "Closed")
        self.as_user(self.content)
        row = self.post(
            "/api/information/",
            {"kind": "notice", "title": "Draft", "body": "Synthetic", "active": False},
        ).json()
        self.assertEqual(self.client.get("/api/information/").json()["count"], 1)
        r = self.client.patch(
            f"/api/information/{row['id']}/", {"title": "Edited"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["title"], "Edited")
        r = self.client.patch(
            f"/api/rules/{self.rule.pk}/", {"active": False}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.as_user(self.student)
        self.assertEqual(self.client.get("/api/rules/").json()["count"], 0)

    def test_staff_lists_and_overview_scopes(self):
        for actor in (
            self.director,
            self.laundry,
            self.mess,
            self.maintenance,
            self.content,
            self.warden,
            self.chief,
            self.student,
        ):
            self.as_user(actor)
            self.assertEqual(self.client.get("/api/overview/").status_code, 200)
        self.as_user(self.director)
        for path in (
            "/api/fees/",
            "/api/payments/attempts/",
            "/api/mess/",
            "/api/mess/coupons/",
            "/api/mess/history/",
            "/api/laundry/allocations/",
            "/api/laundry/records/",
        ):
            self.assertEqual(self.client.get(path).status_code, 200, path)
        self.as_user(self.mess)
        self.assertEqual(self.post("/api/mess/", {}).status_code, 400)

    def test_mess_option_edits_capacity_and_coupon_reassignment(self):
        self.as_user(self.mess)
        row = self.post(
            "/api/mess/options/",
            {"name": "Synthetic", "diet": "Vegetarian", "capacity": 3},
        ).json()
        self.assertIn("id", row)
        url = f"/api/mess/options/{row['id']}/"
        r = self.client.patch(url, {"name": "Empty renamed"}, format="json")
        self.assertEqual(r.status_code, 200)
        for student in (self.student, self.stranger):
            self.assertEqual(
                self.post(
                    "/api/mess/select/", {"student": student.pk, "option": row["id"]}
                ).status_code,
                200,
            )
        self.assertEqual(
            self.client.patch(url, {"name": "Forbidden"}, format="json").status_code,
            400,
        )
        self.assertEqual(
            self.client.patch(url, {"capacity": 1}, format="json").status_code, 400
        )
        self.assertEqual(
            self.client.patch(
                url, {"description": "Updated"}, format="json"
            ).status_code,
            200,
        )
        coupon = self.post(
            "/api/mess/coupons/",
            {
                "student": self.student.pk,
                "code": "BRANCH",
                "valid_from": str(timezone.localdate()),
                "valid_to": str(timezone.localdate()),
            },
        ).json()
        self.assertEqual(
            self.client.patch(
                f"/api/mess/coupons/{coupon['id']}/",
                {"student": self.stranger.pk},
                format="json",
            ).status_code,
            200,
        )
        from apps.student_services.services import select_mess

        option = MessOption.objects.get(pk=row["id"])
        self.student.is_active = False
        self.student.save()
        with self.assertRaises(ValidationError):
            select_mess(self.mess, option, self.student)

    def test_resolved_complaint_cannot_be_reassigned_or_reopened(self):
        row = self.post(
            "/api/complaints/", {"category": "Other", "description": "Synthetic"}
        ).json()
        self.as_user(self.director)
        self.assertEqual(
            self.post(
                f"/api/complaints/{row['id']}/assign/",
                {"assigned_to": self.maintenance.pk},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.post(
                f"/api/complaints/{row['id']}/progress/",
                {"status": "In Progress", "remarks": "Started"},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.post(
                f"/api/complaints/{row['id']}/progress/",
                {"status": "Resolved", "remarks": "Done"},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.post(
                f"/api/complaints/{row['id']}/assign/",
                {"assigned_to": self.maintenance.pk},
            ).status_code,
            400,
        )
        self.assertEqual(
            self.post(
                f"/api/complaints/{row['id']}/progress/",
                {"status": "In Progress", "remarks": "Replay"},
            ).status_code,
            400,
        )


class WorkflowScopes(DomainCase):
    def test_active_and_legacy_scope_adapters_agree(self):
        leave = services.submit_leave(self.student, self.leave_data)
        for module in (permissions, access):
            for actor, expected in (
                (self.student, 1),
                (self.warden, 1),
                (self.chief, 0),
                (self.director, 0),
            ):
                self.assertEqual(
                    module.leave_scope(actor, LeaveRequest.objects.all()).count(),
                    expected,
                )
            for actor in (self.student, self.warden, self.chief, self.director):
                self.assertEqual(
                    module.personal_scope(actor, LeaveRequest.objects.all()).count(),
                    0 if actor == self.director else 1,
                )
                self.assertEqual(
                    module.session_scope(
                        actor, AttendanceSession.objects.all()
                    ).count(),
                    0 if actor == self.director else 1,
                )
            self.assertEqual(module.students_for(self.director).count(), 0)
            self.assertEqual(module.students_for(self.chief).count(), 2)
            self.assertEqual(module.assigned_warden(self.student), self.warden)
            self.assertEqual(module.role(AnonymousUser()), "")
            with self.assertRaises(PermissionDenied):
                module.require(self.director, "STUDENT")
            module.require(self.student, "STUDENT")
            with self.assertRaises(ValidationError):
                module.student_key("invalid")
            self.assertEqual(module.student_key(str(self.student.pk)), self.student.pk)
        services.decide_leave(self.warden, leave.pk, "Escalated", "Review")
        for module in (permissions, access):
            self.assertEqual(
                module.leave_scope(self.chief, LeaveRequest.objects.all()).count(), 1
            )
        self.warden.is_active = False
        self.warden.save()
        for module in (permissions, access):
            self.assertEqual(module.role(self.warden), "")
            with self.assertRaises(ValidationError):
                module.assigned_warden(self.student)

    def test_service_validation_and_missing_staff_filter(self):
        with self.assertRaises(ValidationError):
            services.submit_leave(
                self.student,
                {
                    **self.leave_data,
                    "end_date": self.leave_data["start_date"] - timedelta(days=1),
                },
            )
        row = services.submit_leave(self.student, self.leave_data)
        with self.assertRaises(ValidationError):
            services.decide_leave(self.warden, row.pk, "Unknown", "Bad")
        self.rule.active = False
        self.rule.save()
        with self.assertRaises(ValidationError):
            services.record_deviation(
                self.warden, self.student.pk, self.rule, "Inactive"
            )
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/deviations/total/").status_code, 400)
        self.assertEqual(self.client.get("/api/arin/rules/").status_code, 200)

    def test_boundary_rejections_do_not_create_accepted_attendance(self):
        from apps.leave_attendance.location import check_sample

        now = timezone.now()
        self.session.opens_at = now + timedelta(minutes=1)
        self.assertEqual(
            check_sample(self.session, self.sample, now), (False, "OUTSIDE_WINDOW")
        )
        self.assertEqual(Attendance.objects.filter(result="Accepted").count(), 0)
        with self.assertRaises(ValidationError):
            permissions.assigned_warden(self.director)
        self.as_user(self.warden)
        self.assertEqual(
            self.post(
                "/api/deviations/",
                {"student": self.student.pk, "rule": "invalid", "remarks": "Synthetic"},
            ).status_code,
            400,
        )
        from apps.student_services.services import progress, submit_complaint

        missing = User.objects.create_user(username="unprofiled", role="STUDENT")
        with self.assertRaises(ValidationError):
            submit_complaint(missing, {"category": "Other", "description": "Synthetic"})
        complaint = submit_complaint(
            self.student, {"category": "Other", "description": "Synthetic"}
        )
        with self.assertRaises(ValidationError):
            progress(self.director, complaint.pk, "In Progress", "Unassigned")


@pytest.mark.parametrize("existing", [True, False])
def test_local_settings_create_or_reuse_only_a_local_key(tmp_path, existing):
    from types import ModuleType

    key = tmp_path / "development-key"
    if existing:
        key.write_text("synthetic-local-key")
    source = str(Path(__file__).resolve().parents[1] / "config/settings/local.py")
    environment = {k: v for k, v in os.environ.items() if k != "DJANGO_SECRET_KEY"}
    with (
        patch.dict(os.environ, environment, clear=True),
        patch.dict(
            "sys.modules", {"config.settings.base": ModuleType("config.settings.base")}
        ),
        patch("pathlib.Path") as path,
    ):
        path.return_value.resolve.return_value.parents.__getitem__.return_value.__truediv__.return_value = key
        assert (
            runpy.run_path(source, run_name="config.settings._local_test")["DEBUG"]
            is True
        )
        assert os.environ["DJANGO_SECRET_KEY"] == key.read_text()


def test_serializers_reject_nonobjects_and_invalid_windows():
    from apps.accounts.views import LoginInput
    from apps.information.serializers import RuleSerializer
    from apps.leave_attendance.serializers import SessionInput, StrictInput

    for cls in (LoginInput, RuleSerializer, StrictInput):
        assert not cls(data=[]).is_valid()
    with pytest.raises(PermissionDenied):
        RuleSerializer(data={"id": 1}).is_valid(raise_exception=True)
    body = {
        "title": "Closed",
        "opens_at": timezone.now(),
        "closes_at": timezone.now() - timedelta(minutes=1),
        "centre_latitude": 12,
        "centre_longitude": 77,
        "radius_m": 100,
        "max_accuracy_m": 20,
        "max_sample_age_seconds": 60,
    }
    serializer = SessionInput(data=body)
    assert not serializer.is_valid()
    assert "closes_at" in serializer.errors


@override_settings(DEBUG=True, PAYMENT_MODE="simulation", ALLOW_PAYMENT_SIMULATION=True)
class ProviderBranches(DomainCase):
    def setUp(self):
        super().setUp()
        self.fee = FeeDue.objects.create(
            student=self.student,
            title="Synthetic",
            amount=Decimal("100"),
            due_date=timezone.localdate(),
        )

    def test_disabled_checkout_and_missing_test_credentials(self):
        with override_settings(PAYMENT_MODE="disabled"):
            with self.assertRaises(ValidationError):
                payments.initiate(self.student, self.fee.pk)
        with override_settings(RAZORPAY_KEY_ID="", RAZORPAY_KEY_SECRET=""):
            with self.assertRaises(ValidationError):
                payments.provider_request("orders")

    @override_settings(
        PAYMENT_MODE="razorpay",
        RAZORPAY_KEY_ID="rzp_test_synthetic",
        RAZORPAY_KEY_SECRET="synthetic",
    )
    def test_malformed_provider_orders_and_captured_payloads(self):
        good = {"id": "order_synthetic", "amount": 10000, "currency": "INR"}
        for change in ({"amount": 1}, {"currency": "USD"}, {"id": "invalid"}):
            with patch.object(
                payments, "provider_request", return_value={**good, **change}
            ):
                with self.assertRaises(ValidationError):
                    payments.initiate(self.student, self.fee.pk)
        with patch.object(payments, "provider_request", return_value=good):
            attempt = payments.initiate(self.student, self.fee.pk)
        for pid in ("invalid", "pay_bad!"):
            with self.assertRaises(ValidationError):
                payments.verify(self.student, attempt.pk, pid, "bad")
        signature = hmac.new(
            b"synthetic", b"order_synthetic|pay_synthetic", hashlib.sha256
        ).hexdigest()
        captured = {
            "status": "captured",
            "order_id": attempt.order_id,
            "amount": 10000,
            "currency": "INR",
        }
        for change in (
            {"status": "authorized"},
            {"order_id": "other"},
            {"amount": 1},
            {"currency": "USD"},
        ):
            with patch.object(
                payments, "provider_request", return_value={**captured, **change}
            ):
                with self.assertRaises(ValidationError):
                    payments.verify(
                        self.student, attempt.pk, "pay_synthetic", signature
                    )
        self.fee.refresh_from_db()
        self.assertEqual(self.fee.status, "Unpaid")

    def test_provider_json_transport_and_reference_mismatch(self):
        with override_settings(
            RAZORPAY_KEY_ID="rzp_test_synthetic", RAZORPAY_KEY_SECRET="synthetic"
        ):
            with patch.object(
                payments,
                "urlopen",
                return_value=io.BytesIO(json.dumps({"id": "order_ok"}).encode()),
            ):
                self.assertEqual(payments.provider_request("orders")["id"], "order_ok")
        attempt = payments.initiate(self.student, self.fee.pk)
        payments.finalize(
            attempt.pk,
            self.student,
            "same",
            "Success",
            attempt.amount,
            attempt.currency,
            attempt.order_id,
        )
        with self.assertRaises(ValidationError):
            payments.finalize(
                attempt.pk,
                self.student,
                "different",
                "Success",
                attempt.amount,
                attempt.currency,
                attempt.order_id,
            )


@pytest.mark.django_db
def test_seed_commands_require_local_mode_and_preserve_existing_passwords():
    output = io.StringIO()
    for command in ("seed_demo", "seed_service_demo"):
        with override_settings(DEBUG=False), pytest.raises(CommandError):
            call_command(command, stdout=output)
        with (
            override_settings(DEBUG=True),
            patch.dict(os.environ, {"HOSTELSPACE_DEMO_PASSWORD": "short"}),
            pytest.raises(CommandError),
        ):
            call_command(command, stdout=output)
    with (
        override_settings(DEBUG=True),
        patch.dict(
            os.environ, {"HOSTELSPACE_DEMO_PASSWORD": "Synthetic-unique-78214!"}
        ),
    ):
        call_command("seed_demo", stdout=output)
        student = User.objects.get(username="student")
        original = student.password
        call_command("seed_demo", stdout=output)
        call_command("seed_service_demo", stdout=output)
        call_command("seed_service_demo", stdout=output)
        student.refresh_from_db()
        assert student.password == original
        assert StudentProfile.objects.count() == 2


@pytest.mark.parametrize(
    "handler", ["config.exceptions", "apps.leave_attendance.errors"]
)
def test_error_envelope_handles_unknown_and_list_errors(handler):
    from importlib import import_module

    fn = import_module(handler).api_exception_handler
    assert fn(RuntimeError("unknown"), {}) is None
    response = fn(ValidationError(["Bad input"]), {})
    assert response.status_code == 400
    assert response.data["fields"] == {}
    assert "no-store" in response["Cache-Control"]
    if handler == "config.exceptions":
        assert fn(IntegrityError("conflict"), {}).status_code == 409


@pytest.mark.parametrize(
    "url,sqlite,expected",
    [
        ("postgresql://test@localhost/test", "0", "postgresql"),
        ("", "1", "sqlite3"),
        ("https://localhost/db", "0", None),
        ("postgresql://localhost/db?sslmode=wrong", "0", None),
    ],
)
def test_database_settings_validate_urls_without_connecting(url, sqlite, expected):
    path = Path(__file__).resolve().parents[1] / "config/settings/base.py"
    with patch.dict(os.environ, {"DATABASE_URL": url, "HOSTELSPACE_SQLITE": sqlite}):
        if expected is None:
            with pytest.raises(RuntimeError):
                runpy.run_path(str(path))
        else:
            assert runpy.run_path(str(path))["DATABASES"]["default"]["ENGINE"].endswith(
                expected
            )


@pytest.mark.parametrize(
    "hosts,key,origins,ssl,error",
    [
        ("", "x" * 60, ["https://example.invalid"], "require", "hostnames"),
        ("example.invalid", "short", ["https://example.invalid"], "require", "secret"),
        ("example.invalid", "x" * 60, ["http://example.invalid"], "require", "HTTPS"),
        (
            "example.invalid",
            "x" * 60,
            ["https://example.invalid"],
            "prefer",
            "encrypted",
        ),
        ("example.invalid", "x" * 60, ["https://example.invalid"], "require", None),
    ],
)
def test_production_settings_reject_insecure_configuration(
    hosts, key, origins, ssl, error
):
    from types import ModuleType

    base = ModuleType("config.settings.base")
    base.ALLOWED_HOSTS = hosts.split(",") if hosts else []
    base.SECRET_KEY = key
    base.CSRF_TRUSTED_ORIGINS = origins
    base.DATABASES = {"default": {"OPTIONS": {"sslmode": ssl}}}
    with (
        patch.dict(os.environ, {"DJANGO_ALLOWED_HOSTS": hosts}),
        patch.dict("sys.modules", {"config.settings.base": base}),
    ):
        if error:
            with pytest.raises(RuntimeError, match=error):
                runpy.run_module("config.settings.production")
        else:
            settings = runpy.run_module("config.settings.production")
            assert settings["SESSION_COOKIE_SECURE"] and settings["CSRF_COOKIE_SECURE"]
