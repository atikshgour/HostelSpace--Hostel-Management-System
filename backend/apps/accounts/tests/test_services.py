from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.services import identity


class DomainCase(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        from apps.leave_attendance.tests.test_services import build_fixtures

        build_fixtures(self)
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
