from rest_framework.test import APIClient

from .test_services import DomainCase


class AuthenticationTests(DomainCase):
    def session_client(self):
        c = APIClient(enforce_csrf_checks=True)
        r = c.get("/api/auth/csrf/")
        return c, r.json()["csrfToken"]

    def test_anonymous_apis_require_login(self):
        self.client.force_authenticate(None)
        for p in [
            "/api/auth/me/",
            "/api/information/",
            "/api/fees/",
            "/api/director/users/",
        ]:
            self.assertEqual(self.client.get(p).status_code, 403)

    def test_login_requires_csrf_even_when_anonymous(self):
        c = APIClient(enforce_csrf_checks=True)
        self.assertEqual(
            c.post(
                "/api/auth/login/",
                {"username": "director", "password": "Test-only-random-4779"},
            ).status_code,
            403,
        )

    def test_login_logout_real_session_and_cache(self):
        c, token = self.session_client()
        r = c.post(
            "/api/auth/login/",
            {"username": "director", "password": "Test-only-random-4779"},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("no-store", r["Cache-Control"])
        self.assertEqual(c.get("/api/auth/me/").json()["role"], "DIRECTOR")
        token = c.get("/api/auth/csrf/").json()["csrfToken"]
        self.assertEqual(
            c.post("/api/auth/logout/", {}, HTTP_X_CSRFTOKEN=token).status_code, 200
        )
        self.assertEqual(c.get("/api/auth/me/").status_code, 403)

    def test_invalid_login_is_generic(self):
        c, t = self.session_client()
        r = c.post(
            "/api/auth/login/",
            {"username": "unknown", "password": "wrong"},
            HTTP_X_CSRFTOKEN=t,
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.json()["code"], "invalid_credentials")

    def test_deactivation_revokes_existing_session(self):
        c, t = self.session_client()
        c.post(
            "/api/auth/login/",
            {"username": "director", "password": "Test-only-random-4779"},
            HTTP_X_CSRFTOKEN=t,
        )
        self.director.is_active = False
        self.director.save()
        self.assertEqual(c.get("/api/auth/me/").status_code, 403)

    def test_session_write_requires_csrf(self):
        c, t = self.session_client()
        c.post(
            "/api/auth/login/",
            {"username": "director", "password": "Test-only-random-4779"},
            HTTP_X_CSRFTOKEN=t,
        )
        self.assertEqual(
            c.post(
                "/api/director/settings/", {"key": "site_title", "value": "X"}
            ).status_code,
            403,
        )


class ProfileTests(DomainCase):
    def test_phone_update_persists(self):
        r = self.client.patch(
            "/api/auth/profile/", {"phone": "+91 90000 12345"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.student.student_profile.refresh_from_db()
        self.assertEqual(self.student.student_profile.phone, "+91 90000 12345")

    def test_invalid_phone_rejected(self):
        for phone in ["", "x", "123"]:
            self.assertEqual(
                self.client.patch(
                    "/api/auth/profile/", {"phone": phone}, format="json"
                ).status_code,
                400,
            )

    def test_protected_profile_fields_rejected(self):
        self.assertEqual(
            self.client.patch(
                "/api/auth/profile/",
                {"phone": "9000012345", "role": "DIRECTOR"},
                format="json",
            ).status_code,
            403,
        )

    def test_staff_cannot_edit_student_profile(self):
        self.as_user(self.warden)
        self.assertEqual(self.client.get("/api/auth/profile/").status_code, 403)


class LoginRateTests(DomainCase):
    def test_csrf_bootstrap_does_not_consume_login_rate_bucket(self):
        from django.core.cache import cache

        cache.clear()
        c = APIClient(enforce_csrf_checks=True, REMOTE_ADDR="192.0.2.15")
        for _ in range(12):
            r = c.get("/api/auth/csrf/")
            self.assertEqual(r.status_code, 200)
        token = r.json()["csrfToken"]
        r = c.post(
            "/api/auth/login/",
            {"username": "director", "password": "Test-only-random-4779"},
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(r.status_code, 200)
