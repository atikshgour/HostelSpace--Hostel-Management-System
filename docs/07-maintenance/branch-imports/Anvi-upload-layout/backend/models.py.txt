# Owner: Anvi Srinivas | Story: US-03 | Sprint: 2
from django.conf import settings
from django.db import models


class ContentBase(models.Model):
    """Shared fields. Items are deactivated, never hard-deleted."""
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Notice(ContentBase):
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=5000)


class Contact(ContentBase):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)


class Rule(ContentBase):
    title = models.CharField(max_length=200)
    body = models.TextField(max_length=5000)
    order = models.PositiveIntegerField(default=0)
