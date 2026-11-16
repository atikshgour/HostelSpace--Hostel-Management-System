from django.conf import settings
from django.db import models
from django.db.models import F, Q


class Content(models.Model):
    kind = models.CharField(
        max_length=12,
        choices=[
            ("notice", "Notice"),
            ("information", "Information"),
            ("contact", "Contact"),
        ],
    )
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=5000)
    active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__isnull=True)
                | Q(starts_at__isnull=True)
                | Q(ends_at__gte=F("starts_at")),
                name="content_valid_window",
            )
        ]


class Rule(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=5000, blank=True)
    weightage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(weightage__gte=0), name="rule_nonnegative_weight"
            )
        ]
