from django.test import Client, TestCase

from accounts.models import User

from .models import Notice


class ContentTests(TestCase):
    def setUp(self):
        User.objects.create_user("stu9", password="pass12345", role="student")
        User.objects.create_user("war9", password="pass12345", role="warden")
        User.objects.create_user("mess9", password="pass12345", role="mess")
        self.active = Notice.objects.create(title="Active", body="b")
        self.hidden = Notice.objects.create(title="Hidden", body="b", is_active=False)
        self.c = Client(enforce_csrf_checks=True)

    def _login(self, u):
        t = self.c.get("/api/auth/csrf/").json()["csrfToken"]
        self.c.post("/api/auth/login/", data={"username": u, "password": "pass12345"},
                    content_type="application/json", HTTP_X_CSRFTOKEN=t)
        return self.c.get("/api/auth/csrf/").json()["csrfToken"]

    def _send(self, method, url, body, t):
        return getattr(self.c, method)(url, data=body, content_type="application/json",
                                       HTTP_X_CSRFTOKEN=t)

    def test_anonymous_401(self):
        self.assertEqual(self.c.get("/api/content/notices/").status_code, 401)

    def test_student_sees_only_active(self):
        self._login("stu9")
        titles = [i["title"] for i in self.c.get("/api/content/notices/").json()["items"]]
        self.assertEqual(titles, ["Active"])

    def test_non_housekeeping_staff_sees_only_active(self):
        self._login("mess9")
        self.assertEqual(len(self.c.get("/api/content/notices/").json()["items"]), 1)

    def test_warden_sees_all(self):
        self._login("war9")
        self.assertEqual(len(self.c.get("/api/content/notices/").json()["items"]), 2)

    def test_student_cannot_create_or_edit(self):
        t = self._login("stu9")
        self.assertEqual(self._send("post", "/api/content/notices/", {"title": "x", "body": "y"}, t).status_code, 403)
        self.assertEqual(self._send("patch", f"/api/content/notices/{self.active.id}/", {"title": "z"}, t).status_code, 403)

    def test_warden_create_notice(self):
        t = self._login("war9")
        r = self._send("post", "/api/content/notices/", {"title": "Water cut", "body": "Tomorrow 9-11"}, t)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Notice.objects.get(title="Water cut").created_by.username, "war9")

    def test_validation(self):
        t = self._login("war9")
        r = self._send("post", "/api/content/notices/", {"title": "", "extra": 1}, t)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.json()["fields"]), {"title", "body", "extra"})

    def test_deactivate_hides_from_student(self):
        t = self._login("war9")
        r = self._send("patch", f"/api/content/notices/{self.active.id}/", {"is_active": False}, t)
        self.assertEqual(r.status_code, 200)
        c2 = Client()
        c2.login(username="stu9", password="pass12345")
        self.assertEqual(c2.get("/api/content/notices/").json()["items"], [])

    def test_contact_phone_and_email_validation(self):
        t = self._login("war9")
        bad = self._send("post", "/api/content/contacts/",
                         {"name": "A", "designation": "Warden", "phone": "12", "email": "nope"}, t)
        self.assertEqual(set(bad.json()["fields"]), {"phone", "email"})
        ok = self._send("post", "/api/content/contacts/",
                        {"name": "A", "designation": "Warden", "phone": "9876543210"}, t)
        self.assertEqual(ok.status_code, 201)

    def test_rules_order(self):
        t = self._login("war9")
        self._send("post", "/api/content/rules/", {"title": "B", "body": "x", "order": 2}, t)
        self._send("post", "/api/content/rules/", {"title": "A", "body": "x", "order": 1}, t)
        titles = [i["title"] for i in self.c.get("/api/content/rules/").json()["items"]]
        self.assertEqual(titles, ["A", "B"])

    def test_unknown_kind_404(self):
        self._login("war9")
        self.assertEqual(self.c.get("/api/content/unknown/").status_code, 404)

    def test_post_without_csrf(self):
        self._login("war9")
        self.assertEqual(self._send("post", "/api/content/notices/", {"title": "x", "body": "y"}, "").status_code, 403)
