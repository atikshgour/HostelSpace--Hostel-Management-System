from apps.accounts.models import AuditEvent, User
from apps.accounts.tests.test_services import DomainCase


class DirectorTests(DomainCase):
    def new(self, **kw):
        return self.post(
            "/api/director/users/",
            {
                "username": "newstudent",
                "password": "Random-test-password-8279",
                "role": "STUDENT",
                "srn": "NEW-1",
                "room": "205",
                "assigned_warden": self.warden.pk,
                **kw,
            },
        )

    def test_student_cannot_manage_accounts_or_reports(self):
        for p in [
            "/api/director/users/",
            "/api/director/settings/",
            "/api/director/summary/",
        ]:
            self.assertEqual(self.client.get(p).status_code, 403)

    def test_director_creates_student_with_assignment(self):
        self.as_user(self.director)
        self.assertEqual(self.new().status_code, 201)
        u = User.objects.get(username="newstudent")
        self.assertEqual(u.student_profile.assigned_warden, self.warden)
        self.assertEqual(u.student_profile.room, "205")

    def test_warden_cannot_create_operational_accounts(self):
        self.as_user(self.warden)
        self.assertEqual(self.new().status_code, 403)

    def test_director_can_create_each_service_staff_type(self):
        self.as_user(self.director)
        for role in [
            "LAUNDRY_STAFF",
            "MAINTENANCE_STAFF",
            "MESS_STAFF",
            "CONTENT_STAFF",
        ]:
            r = self.post(
                "/api/director/users/",
                {
                    "username": "new" + role,
                    "role": role,
                    "password": "Random-test-password-8279",
                },
            )
            self.assertEqual(r.status_code, 201)
            self.assertEqual(
                User.objects.get(pk=r.json()["id"]).managed_by, self.director
            )

    def test_cannot_create_privileged_roles_or_spoof_assignments(self):
        self.as_user(self.warden)
        for role in ["DIRECTOR", "WARDEN", "CHIEF_WARDEN"]:
            self.assertEqual(self.new(role=role).status_code, 403)
        self.assertEqual(self.new(assigned_warden=self.other.pk).status_code, 403)
        self.assertEqual(self.new(is_superuser=True).status_code, 403)

    def test_password_validation_and_duplicate_username(self):
        self.as_user(self.director)
        self.assertEqual(self.new(password="123").status_code, 400)
        self.assertEqual(self.new(username="student").status_code, 400)

    def test_warden_cannot_list_or_edit_accounts(self):
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/director/users/").status_code, 403)
        self.assertEqual(
            self.client.patch(
                f"/api/director/users/{self.student.pk}/", {"room": "1"}, format="json"
            ).status_code,
            403,
        )

    def test_cannot_deactivate_self_or_assigned_warden(self):
        self.as_user(self.director)
        for u in [self.director, self.warden]:
            self.assertEqual(
                self.client.patch(
                    f"/api/director/users/{u.pk}/", {"is_active": False}, format="json"
                ).status_code,
                400,
            )

    def test_invalid_assignment_rejected(self):
        self.as_user(self.director)
        self.assertEqual(
            self.client.patch(
                f"/api/director/users/{self.student.pk}/",
                {"assigned_warden": self.mess.pk},
                format="json",
            ).status_code,
            400,
        )

    def test_settings_allowlist_and_audit(self):
        self.as_user(self.director)
        self.assertEqual(
            self.post(
                "/api/director/settings/",
                {"key": "site_title", "value": "Campus portal"},
            ).status_code,
            200,
        )
        self.assertEqual(
            self.post(
                "/api/director/settings/", {"key": "payment_secret", "value": "x"}
            ).status_code,
            400,
        )
        self.assertTrue(AuditEvent.objects.filter(action="setting_updated").exists())

    def test_reports_counts_use_source_rows(self):
        self.as_user(self.director)
        r = self.client.get("/api/director/summary/").json()
        self.assertEqual(r["active_students"], 2)
        self.assertEqual(r["pending_leave"], 0)

    def test_warden_overview_scopes_active_students(self):
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/overview/").json()["active_students"], 1)

    def test_choice_directory_scopes_students(self):
        self.as_user(self.warden)
        self.assertEqual(
            [x["id"] for x in self.client.get("/api/choices/users/").json()["results"]],
            [self.student.pk],
        )

    def test_service_staff_overview_does_not_expose_fee_or_leave_counts(self):
        for u in [self.laundry, self.mess, self.maintenance, self.content]:
            self.as_user(u)
            data = self.client.get("/api/overview/").json()
            self.assertNotIn("unpaid_fees", data)
            self.assertNotIn("pending_leave", data)

    def test_warden_and_chief_overview_excludes_other_domains(self):
        for user in (self.warden, self.chief):
            self.as_user(user)
            data = self.client.get("/api/overview/").json()
            for field in (
                "unpaid_fees",
                "open_complaints",
                "laundry_received",
                "laundry_ready",
            ):
                self.assertNotIn(field, data)
