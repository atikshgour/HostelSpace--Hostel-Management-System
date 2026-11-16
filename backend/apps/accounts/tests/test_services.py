# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import StudentProfile, User
from apps.accounts.services import identity


class DomainCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        self.chief = User.objects.create_user(username="chief", role="CHIEF_WARDEN")
        self.warden = User.objects.create_user(
            username="warden", role="WARDEN", chief_warden=self.chief
        )
        self.other = User.objects.create_user(
            username="other", role="WARDEN", chief_warden=self.chief
        )
        self.student = User.objects.create_user(username="student", role="STUDENT")
        self.stranger = User.objects.create_user(username="stranger", role="STUDENT")
        StudentProfile.objects.create(
            user=self.student, srn="TEST-001", room="T-1", assigned_warden=self.warden
        )
        StudentProfile.objects.create(
            user=self.stranger, srn="TEST-002", room="T-2", assigned_warden=self.other
        )
        self.director = User.objects.create_user(
            username="director", password="Test-only-random-4779", role="DIRECTOR"
        )
        self.laundry = User.objects.create_user(
            username="laundry", role="LAUNDRY_STAFF"
        )
        self.maintenance = User.objects.create_user(
            username="maintenance", role="MAINTENANCE_STAFF"
        )
        self.mess = User.objects.create_user(username="mess", role="MESS_STAFF")
        self.content = User.objects.create_user(
            username="content", role="CONTENT_STAFF"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.student)

    def as_user(self, user):
        self.client.force_authenticate(user)

    def post(self, path, data):
        return self.client.post(path, data, format="json")


class AccountModelTests(DomainCase):
    def test_single_active_chief_database_constraint(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(username="chief2", role="CHIEF_WARDEN")

    def test_inactive_chief_can_coexist(self):
        u = User.objects.create_user(
            username="chief2", role="CHIEF_WARDEN", is_active=False
        )
        self.assertFalse(u.is_active)

    def test_identity_omits_secrets(self):
        d = identity(self.director)
        self.assertNotIn("password", d)
        self.assertEqual(d["role"], "DIRECTOR")
