# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        WARDEN = "WARDEN", "Warden"
        CHIEF_WARDEN = "CHIEF_WARDEN", "Chief Warden"
        DIRECTOR = "DIRECTOR", "Director"
        LAUNDRY_STAFF = "LAUNDRY_STAFF", "Laundry Staff"
        MAINTENANCE_STAFF = "MAINTENANCE_STAFF", "Maintenance Staff"
        MESS_STAFF = "MESS_STAFF", "Mess Staff"
        CONTENT_STAFF = "CONTENT_STAFF", "Content Staff"

    managed_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="managed_accounts",
    )
    role = models.CharField(max_length=24, choices=Role.choices, default=Role.STUDENT)
    chief_warden = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="wardens"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role"],
                condition=Q(role="CHIEF_WARDEN", is_active=True),
                name="one_active_chief",
            )
        ]


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name="student_profile"
    )
    srn = models.CharField(max_length=40, unique=True)
    hostel = models.CharField(max_length=80, default="Block A")
    room = models.CharField(max_length=30)
    phone = models.CharField(max_length=20, blank=True)
    assigned_warden = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_students",
    )


class SiteSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=500)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)


class AuditEvent(models.Model):
    actor = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=80)
    object_key = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-pk"]
