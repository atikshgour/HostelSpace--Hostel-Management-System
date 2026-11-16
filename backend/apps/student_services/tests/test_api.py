# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
from datetime import timedelta

from django.utils import timezone

from apps.accounts.tests.test_services import DomainCase
from apps.student_services.models import (
    Complaint,
    Coupon,
    MessOption,
)


class ComplaintTests(DomainCase):
    def create(self):
        return self.post(
            "/api/complaints/",
            {"category": "Electrical", "description": "Lamp not working"},
        )

    def test_room_and_student_derived_on_server(self):
        r = self.create()
        self.assertEqual(r.status_code, 201)
        self.assertIn("T-1", r.json()["room_snapshot"])
        self.assertEqual(r.json()["student"], self.student.pk)

    def test_invalid_category_and_empty_description(self):
        self.assertEqual(
            self.post(
                "/api/complaints/", {"category": "Unknown", "description": "X"}
            ).status_code,
            400,
        )
        self.assertEqual(
            self.post(
                "/api/complaints/", {"category": "Other", "description": ""}
            ).status_code,
            400,
        )

    def test_spoofed_student_rejected(self):
        self.assertEqual(
            self.post(
                "/api/complaints/",
                {"category": "Other", "description": "X", "student": self.stranger.pk},
            ).status_code,
            403,
        )

    def test_student_scope_in_list_and_detail(self):
        pk = self.create().json()["id"]
        self.as_user(self.stranger)
        self.assertEqual(self.client.get("/api/complaints/").json()["results"], [])
        self.assertEqual(self.client.get(f"/api/complaints/{pk}/").status_code, 404)

    def test_only_director_assigns_active_maintenance(self):
        pk = self.create().json()["id"]
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/assign/", {"assigned_to": self.maintenance.pk}
            ).status_code,
            403,
        )
        self.as_user(self.director)
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/assign/", {"assigned_to": self.warden.pk}
            ).status_code,
            400,
        )

    def test_full_progress_and_history_no_revert(self):
        pk = self.create().json()["id"]
        self.as_user(self.director)
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/assign/", {"assigned_to": self.maintenance.pk}
            ).status_code,
            200,
        )
        self.as_user(self.maintenance)
        for status in ["In Progress", "Resolved"]:
            self.assertEqual(
                self.post(
                    f"/api/complaints/{pk}/progress/",
                    {"status": status, "remarks": "Checked"},
                ).status_code,
                200,
            )
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/progress/",
                {"status": "In Progress", "remarks": "Reopen"},
            ).status_code,
            400,
        )
        self.assertEqual(Complaint.objects.get(pk=pk).transitions.count(), 4)

    def test_unassigned_staff_has_no_access(self):
        pk = self.create().json()["id"]
        self.as_user(self.maintenance)
        self.assertEqual(self.client.get(f"/api/complaints/{pk}/").status_code, 404)
        self.assertEqual(
            self.post(
                f"/api/complaints/{pk}/progress/",
                {"status": "In Progress", "remarks": "X"},
            ).status_code,
            403,
        )


class MessTests(DomainCase):
    def test_students_cannot_assign(self):
        self.assertEqual(
            self.post(
                "/api/mess/", {"student": self.student.pk, "mess_name": "Main"}
            ).status_code,
            403,
        )

    def test_mess_staff_assigns_personal_allocation(self):
        self.as_user(self.mess)
        o = MessOption.objects.create(name="Test hall", diet="Vegetarian")
        self.assertEqual(
            self.post(
                "/api/mess/select/", {"student": self.student.pk, "option": o.pk}
            ).status_code,
            200,
        )
        self.as_user(self.stranger)
        self.assertEqual(self.client.get("/api/mess/").json()["results"], [])

    def test_current_coupon_filter_and_owner_scope(self):
        today = timezone.localdate()
        for code, student, active, offset in [
            ("GOOD", self.student, True, 1),
            ("OLD", self.student, True, -1),
            ("INACTIVE", self.student, False, 1),
            ("OTHER", self.stranger, True, 1),
        ]:
            Coupon.objects.create(
                code=code,
                student=student,
                active=active,
                valid_from=today - timedelta(days=2),
                valid_to=today + timedelta(days=offset),
                created_by=self.mess,
            )
        self.assertEqual(
            [
                x["code"]
                for x in self.client.get("/api/mess/coupons/").json()["results"]
            ],
            ["GOOD"],
        )

    def test_invalid_coupon_range(self):
        self.as_user(self.mess)
        self.assertEqual(
            self.post(
                "/api/mess/coupons/",
                {
                    "student": self.student.pk,
                    "code": "X",
                    "valid_from": "2026-10-02",
                    "valid_to": "2026-10-01",
                },
            ).status_code,
            400,
        )

    def test_blank_coupon_rejected(self):
        self.as_user(self.mess)
        self.assertEqual(
            self.post(
                "/api/mess/coupons/",
                {
                    "student": self.student.pk,
                    "code": "",
                    "valid_from": "2026-10-01",
                    "valid_to": "2026-10-02",
                },
            ).status_code,
            400,
        )
