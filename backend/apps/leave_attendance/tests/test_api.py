"""Arin Singh | US-05–08 and US-22 scoped API tests."""
import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from apps.leave_attendance import services
from apps.leave_attendance.models import Attendance, Deviation
from .test_services import build_fixtures

class ApiTests(TestCase):
    def setUp(self):
        build_fixtures(self)
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def test_anonymous_and_nonworkflow_roles_are_denied(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/leaves/").status_code, 403)
        self.student.role = "DIRECTOR"
        self.student.save(update_fields=["role"])
        self.client.force_authenticate(self.student)
        for path in ("/api/leaves/", "/api/attendance/history/", "/api/deviations/"):
            self.assertEqual(self.client.get(path).status_code, 403)

    def test_create_leave_and_private_cache_headers(self):
        response = self.client.post("/api/leaves/", self.leave_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("no-store", response["Cache-Control"])

    def test_protected_fields_and_bad_dates_are_rejected(self):
        protected = self.client.post("/api/leaves/", {**self.leave_data, "student": self.stranger.pk}, format="json")
        self.assertEqual(protected.status_code, 403)
        invalid = self.client.post("/api/leaves/", {**self.leave_data, "end_date": "2000-01-01"}, format="json")
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("fields", invalid.json())

    def test_leave_scope_and_decision_scope(self):
        row = services.submit_leave(self.stranger, self.leave_data)
        self.assertEqual(self.client.get(f"/api/leaves/{row.pk}/").status_code, 404)
        own = services.submit_leave(self.student, self.leave_data)
        self.client.force_authenticate(self.other)
        response = self.client.post(f"/api/leaves/{own.pk}/decision/", {"decision": "Approved", "remarks": "OK"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_chief_reads_only_escalated_or_self_finalized_requests(self):
        row = services.submit_leave(self.student, self.leave_data)
        self.client.force_authenticate(self.chief)
        self.assertEqual(self.client.get(f"/api/leaves/{row.pk}/").status_code, 404)
        services.decide_leave(self.warden, row.pk, "Escalated", "Review")
        self.assertEqual(self.client.get(f"/api/leaves/{row.pk}/").status_code, 200)
        services.decide_leave(self.chief, row.pk, "Approved", "OK")
        self.assertEqual(self.client.get(f"/api/leaves/{row.pk}/").status_code, 200)

    def test_attendance_submission_does_not_echo_coordinates(self):
        response = self.client.post("/api/attendance/submit/", {"session": str(self.session.pk), **self.sample}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["result"], "Accepted")
        self.assertNotIn("latitude", response.json())
        self.assertEqual(Attendance.objects.count(), 1)

    def test_invalid_or_unassigned_attendance_is_rejected(self):
        for value in (91, "NaN", "Infinity"):
            response = self.client.post("/api/attendance/submit/", {"session": str(self.session.pk), **self.sample, "latitude": value}, format="json")
            self.assertEqual(response.status_code, 400)
        self.client.force_authenticate(self.stranger)
        response = self.client.post("/api/attendance/submit/", {"session": str(self.session.pk), **self.sample}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_deviation_snapshot_total_and_retained_deactivation(self):
        self.client.force_authenticate(self.warden)
        response = self.client.post("/api/deviations/", {"student": str(self.student.pk), "rule": str(self.rule.pk), "remarks": "Observed"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["weightage_snapshot"], "2.50")
        total_url = f"/api/deviations/total/?student={self.student.pk}"
        self.assertEqual(self.client.get(total_url).json()["active_total"], "2.50")
        self.client.post(f"/api/deviations/{response.json()['id']}/deactivate/", {"reason": "Correction"}, format="json")
        self.assertEqual(self.client.get(total_url).json()["active_total"], "0.00")
        self.assertEqual(Deviation.objects.count(), 1)

    def test_deviation_permissions_and_server_owned_weight(self):
        self.assertEqual(self.client.post("/api/deviations/", {}, format="json").status_code, 403)
        self.client.force_authenticate(self.warden)
        response = self.client.post("/api/deviations/", {"student": str(self.student.pk), "rule": str(self.rule.pk), "remarks": "Observed", "weightage_snapshot": "0"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.client.force_authenticate(self.other)
        response = self.client.post("/api/deviations/", {"student": str(self.student.pk), "rule": str(self.rule.pk), "remarks": "Observed"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_choices_are_scoped_and_staff_only(self):
        self.assertEqual(self.client.get("/api/arin/students/").status_code, 403)
        self.client.force_authenticate(self.warden)
        rows = self.client.get("/api/arin/students/").json()["results"]
        self.assertEqual([str(row["id"]) for row in rows], [str(self.student.pk)])

    def test_unknown_and_malformed_identifiers(self):
        self.assertEqual(self.client.get(f"/api/leaves/{uuid.uuid4()}/").status_code, 404)
        self.client.force_authenticate(self.warden)
        self.assertEqual(self.client.get("/api/deviations/total/?student=invalid").status_code, 400)
        self.assertEqual(self.client.post("/api/deviations/", {"student": "invalid", "rule": str(self.rule.pk), "remarks": "Test"}, format="json").status_code, 400)

    def test_pagination_is_bounded(self):
        for _ in range(26):
            services.submit_leave(self.student, self.leave_data)
        response = self.client.get("/api/leaves/").json()
        self.assertEqual(len(response["results"]), 25)
        self.assertIsNotNone(response["next"])
