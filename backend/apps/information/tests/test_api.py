from datetime import timedelta

from django.utils import timezone

from apps.accounts.tests.test_services import DomainCase
from apps.information.models import Content, Rule


class InformationTests(DomainCase):
    def test_student_reads_only_active_current_notices(self):
        now = timezone.now()
        for title, extra in [
            ("Current", {}),
            ("Inactive", {"active": False}),
            ("Future", {"starts_at": now + timedelta(days=1)}),
            ("Expired", {"ends_at": now - timedelta(days=1)}),
        ]:
            Content.objects.create(
                kind="notice",
                title=title,
                body="Text",
                updated_by=self.director,
                **extra,
            )
        r = self.client.get("/api/information/")
        self.assertEqual([x["title"] for x in r.json()["results"]], ["Current"])

    def test_student_cannot_publish(self):
        self.assertEqual(self.post("/api/information/", {}).status_code, 403)

    def test_authorized_staff_create_and_edit(self):
        self.as_user(self.content)
        r = self.post(
            "/api/information/", {"kind": "notice", "title": "New", "body": "Body"}
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(
            self.client.patch(
                f"/api/information/{r.json()['id']}/", {"active": False}, format="json"
            ).status_code,
            200,
        )

    def test_invalid_notice_dates_rejected(self):
        self.as_user(self.director)
        now = timezone.now()
        r = self.post(
            "/api/information/",
            {
                "kind": "notice",
                "title": "N",
                "body": "B",
                "starts_at": now.isoformat(),
                "ends_at": (now - timedelta(days=1)).isoformat(),
            },
        )
        self.assertEqual(r.status_code, 400)

    def test_empty_title_rejected(self):
        self.as_user(self.director)
        self.assertEqual(
            self.post(
                "/api/information/", {"kind": "notice", "title": " ", "body": "B"}
            ).status_code,
            400,
        )

    def test_rule_negative_weight_rejected(self):
        self.as_user(self.content)
        self.assertEqual(
            self.post("/api/rules/", {"title": "R", "weightage": "-1"}).status_code, 400
        )

    def test_rule_deactivation_retains_id(self):
        self.as_user(self.director)
        r = self.client.patch(
            f"/api/rules/{self.rule.pk}/", {"active": False}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(Rule.objects.filter(pk=self.rule.pk).exists())

    def test_warden_cannot_publish_or_rewrite_rules(self):
        self.as_user(self.warden)
        self.assertEqual(
            self.post(
                "/api/information/",
                {"kind": "notice", "title": "Forbidden", "body": "Body"},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/rules/{self.rule.pk}/", {"weightage": "99.00"}, format="json"
            ).status_code,
            403,
        )
