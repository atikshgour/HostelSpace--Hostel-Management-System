"""Arin Singh | US-05–08 and US-22 service/constraint tests.

These tests intentionally use the shared accounts.User, StudentProfile and
information.Rule contracts. They become executable after those owner modules
replace their starter placeholders.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal
from threading import Barrier
from unittest import skipUnless

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from apps.leave_attendance import services
from apps.leave_attendance.location import check_sample, distance_m
from apps.leave_attendance.models import Attendance, AttendanceSession


def build_fixtures(case):
    User = get_user_model()
    Profile = apps.get_model("accounts", "StudentProfile")
    Rule = apps.get_model("information", "Rule")
    case.chief = User.objects.create_user(username="chief", role="CHIEF_WARDEN")
    case.warden = User.objects.create_user(username="warden", role="WARDEN", chief_warden=case.chief)
    case.other = User.objects.create_user(username="other", role="WARDEN", chief_warden=case.chief)
    case.student = User.objects.create_user(username="student", role="STUDENT")
    case.stranger = User.objects.create_user(username="stranger", role="STUDENT")
    Profile.objects.create(user=case.student, srn="TEST-001", room="T-1", assigned_warden=case.warden)
    Profile.objects.create(user=case.stranger, srn="TEST-002", room="T-2", assigned_warden=case.other)
    case.rule = Rule.objects.create(title="Test rule", weightage=Decimal("2.50"), active=True)
    now = timezone.now()
    case.session = AttendanceSession.objects.create(
        title="Test session", warden=case.warden,
        opens_at=now-timedelta(minutes=5), closes_at=now+timedelta(minutes=5),
        centre_latitude=12.0, centre_longitude=77.0, radius_m=100,
        max_accuracy_m=50, max_sample_age_seconds=60,
    )
    case.sample = {"latitude": 12.0, "longitude": 77.0, "accuracy_m": 5, "sampled_at": now}
    case.leave_data = {"start_date": now.date(), "end_date": now.date()+timedelta(days=1), "reason": "Family visit"}


class ServiceTests(TestCase):
    def setUp(self):
        build_fixtures(self)

    def test_leave_submission_records_actor_and_assignment(self):
        row = services.submit_leave(self.student, self.leave_data)
        self.assertEqual(row.status, "Pending")
        self.assertEqual(row.assigned_warden, self.warden)
        self.assertEqual(row.transitions.get().actor, self.student)

    def test_only_student_submits(self):
        with self.assertRaises(PermissionDenied):
            services.submit_leave(self.warden, self.leave_data)

    def test_escalation_then_chief_finalization(self):
        row = services.submit_leave(self.student, self.leave_data)
        services.decide_leave(self.warden, row.pk, "Escalated", "Review required")
        services.decide_leave(self.chief, row.pk, "Approved", "Reviewed")
        row.refresh_from_db()
        self.assertEqual(row.status, "Approved")
        self.assertEqual(row.transitions.count(), 3)

    def test_final_decision_is_immutable(self):
        row = services.submit_leave(self.student, self.leave_data)
        services.decide_leave(self.warden, row.pk, "Rejected", "Not permitted")
        with self.assertRaises(services.Conflict):
            services.decide_leave(self.warden, row.pk, "Approved", "Changed")
        self.assertEqual(row.transitions.count(), 2)

    def test_warden_cannot_finalize_escalated_request(self):
        row = services.submit_leave(self.student, self.leave_data)
        services.decide_leave(self.warden, row.pk, "Escalated", "Review")
        with self.assertRaises(PermissionDenied):
            services.decide_leave(self.warden, row.pk, "Approved", "Changed")

    def test_one_accepted_attendance_and_rejected_retry(self):
        rejected = services.submit_attendance(self.student, self.session.pk, {**self.sample, "accuracy_m": 100})
        self.assertEqual(rejected.reason_code, "LOW_ACCURACY")
        services.submit_attendance(self.student, self.session.pk, self.sample)
        with self.assertRaises(services.Conflict):
            services.submit_attendance(self.student, self.session.pk, self.sample)
        self.assertEqual(Attendance.objects.filter(result="Accepted").count(), 1)

    def test_database_prevents_second_acceptance(self):
        Attendance.objects.create(student=self.student, session=self.session, result="Accepted", reason_code="WITHIN_POLICY")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Attendance.objects.create(student=self.student, session=self.session, result="Accepted", reason_code="WITHIN_POLICY")

    def test_raw_student_sample_is_not_persisted(self):
        fields = {field.name for field in Attendance._meta.get_fields()}
        self.assertFalse(fields & {"latitude", "longitude", "accuracy_m", "distance", "sampled_at"})

    def test_location_boundaries(self):
        for now in (self.session.opens_at, self.session.closes_at):
            sample = {**self.sample, "sampled_at": now, "accuracy_m": self.session.max_accuracy_m}
            self.assertEqual(check_sample(self.session, sample, now), (True, "WITHIN_POLICY"))
        now = timezone.now()
        stale = {**self.sample, "sampled_at": now-timedelta(seconds=61)}
        self.assertEqual(check_sample(self.session, stale, now), (False, "STALE_SAMPLE"))
        outside = {**self.sample, "latitude": 13}
        self.assertEqual(check_sample(self.session, outside, now), (False, "OUTSIDE_RADIUS"))
        self.assertAlmostEqual(distance_m(0, 0, 0, 1), 111195, delta=5)

    def test_deviation_snapshot_and_deactivation_history(self):
        row = services.record_deviation(self.warden, self.student.pk, self.rule, "Observed")
        self.rule.weightage = Decimal("99")
        self.rule.save()
        row.refresh_from_db()
        self.assertEqual(row.weightage_snapshot, Decimal("2.50"))
        services.deactivate_deviation(self.warden, row.pk, "Correction")
        row.refresh_from_db()
        self.assertFalse(row.active)
        self.assertEqual(row.deactivated_by, self.warden)
        with self.assertRaises(services.Conflict):
            services.deactivate_deviation(self.warden, row.pk, "Again")


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locking and partial uniqueness.")
class ConcurrentTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        build_fixtures(self)

    def race(self, operation):
        barrier = Barrier(2)
        def worker():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    operation()
                    return "ok"
                except services.Conflict:
                    return "conflict"
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: worker(), range(2)))
        self.assertCountEqual(results, ["ok", "conflict"])

    def test_concurrent_attendance_accepts_once(self):
        User = get_user_model()
        self.race(lambda: services.submit_attendance(User.objects.get(pk=self.student.pk), self.session.pk, self.sample))
        self.assertEqual(Attendance.objects.filter(result="Accepted").count(), 1)

    def test_concurrent_leave_finalizes_once(self):
        User = get_user_model()
        row = services.submit_leave(self.student, self.leave_data)
        self.race(lambda: services.decide_leave(User.objects.get(pk=self.warden.pk), row.pk, "Approved", "Reviewed"))
        row.refresh_from_db()
        self.assertEqual(row.status, "Approved")
        self.assertEqual(row.transitions.count(), 2)
