from datetime import date, timedelta

from django.utils import timezone

from apps.accounts.tests.test_services import DomainCase
from apps.facilities.models import LaundryRecord
from apps.facilities.services import collect, ready, schedule


class FacilitiesTests(DomainCase):
    def receive(self, **extra):
        self.as_user(self.laundry)
        return self.post(
            "/api/laundry/records/",
            {
                "student": self.student.pk,
                "item_details": "Shirts",
                "item_count": 3,
                **extra,
            },
        )

    def test_authorized_director_updates_study(self):
        self.assertEqual(
            self.client.put(
                "/api/study-room/", {"status": "Open"}, format="json"
            ).status_code,
            403,
        )
        self.as_user(self.director)
        self.assertEqual(
            self.client.put(
                "/api/study-room/", {"status": "Open"}, format="json"
            ).status_code,
            200,
        )

    def test_invalid_study_status(self):
        self.as_user(self.content)
        self.assertEqual(
            self.client.put(
                "/api/study-room/", {"status": "Booked"}, format="json"
            ).status_code,
            400,
        )

    def test_manual_allocation_disabled_for_every_role(self):
        for u in [self.student, self.warden, self.laundry]:
            self.as_user(u)
            self.assertEqual(
                self.post(
                    "/api/laundry/allocations/",
                    {"student": self.student.pk, "weekday": "Monday"},
                ).status_code,
                403,
            )

    def test_number_modulo_schedule_and_stability(self):
        p = schedule(self.student, today=date(2026, 10, 27))
        self.assertEqual(p["group_number"], 1)
        self.assertEqual(p["weekday"], "Monday")
        self.assertEqual(p["next_dropoff_date"], date(2026, 11, 2))
        self.assertEqual(p["next_return_date"], date(2026, 11, 5))
        self.stranger.is_active = False
        self.stranger.save()
        self.assertEqual(schedule(self.student)["group_number"], 1)

    def test_student_schedule_is_owned_and_warden_is_denied(self):
        self.assertEqual(
            [
                x["student"]
                for x in self.client.get("/api/laundry/allocations/").json()["results"]
            ],
            [self.student.pk],
        )
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/laundry/allocations/").status_code, 403)

    def test_positive_whole_item_count(self):
        for n in [0, -1, 1.5, "x"]:
            self.assertEqual(self.receive(item_count=n).status_code, 400)

    def test_receive_without_manual_allocation(self):
        r = self.receive()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(
            r.json()["expected_return_date"],
            str(timezone.localdate() + timedelta(days=3)),
        )

    def test_selected_turnaround_and_invalid_bounds(self):
        self.assertEqual(
            self.receive(turnaround_days=5).json()["expected_return_date"],
            str(timezone.localdate() + timedelta(days=5)),
        )
        for n in [0, 15, 1.5]:
            self.assertEqual(self.receive(turnaround_days=n).status_code, 400)

    def test_policy_change_affects_future_only(self):
        old = self.receive().json()
        self.assertEqual(
            self.client.put(
                "/api/laundry/policy/", {"turnaround_days": 6}, format="json"
            ).status_code,
            200,
        )
        new = self.receive().json()
        self.assertEqual(
            new["expected_return_date"], str(timezone.localdate() + timedelta(days=6))
        )
        self.assertEqual(
            LaundryRecord.objects.get(pk=old["id"]).expected_return_date,
            timezone.localdate() + timedelta(days=3),
        )

    def test_only_laundry_staff_changes_policy(self):
        self.as_user(self.warden)
        self.assertEqual(
            self.client.put(
                "/api/laundry/policy/", {"turnaround_days": 4}, format="json"
            ).status_code,
            403,
        )

    def test_ready_then_collection_idempotent(self):
        r = self.receive().json()
        ready(self.laundry, r["id"])
        a = collect(self.laundry, r["id"])
        first = a.collected_at
        a = collect(self.laundry, r["id"])
        self.assertEqual(a.collected_at, first)
        self.assertEqual(a.received_by, self.laundry)
        self.assertEqual(LaundryRecord.objects.count(), 1)

    def test_cannot_collect_before_ready(self):
        r = self.receive().json()
        self.assertEqual(
            self.post(f"/api/laundry/records/{r['id']}/collect/", {}).status_code, 400
        )

    def test_student_cannot_transition_or_read_other_batches(self):
        r = self.receive().json()
        self.as_user(self.stranger)
        self.assertEqual(self.client.get("/api/laundry/records/").json()["results"], [])
        for action in ["ready", "collect"]:
            self.assertEqual(
                self.post(f"/api/laundry/records/{r['id']}/{action}/", {}).status_code,
                403,
            )


class PdfPermissionTests(DomainCase):
    def test_warden_has_no_laundry_or_study_management_permission(self):
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/laundry/records/").status_code, 403)
        self.assertEqual(
            self.client.put(
                "/api/study-room/", {"status": "Open"}, format="json"
            ).status_code,
            403,
        )
