# Minimal dependency for US-13, authorized by user | Owner: Anvi Srinivas
# US-01/02 foundation; original SRS Sprint 1 | Independent review pending
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        WARDEN = 'warden', 'Warden'
        CHIEF_WARDEN = 'chief_warden', 'Chief Warden'
        HOSTEL_DIRECTOR = 'hostel_director', 'Hostel Director'
        MAINTENANCE = 'maintenance_staff', 'Maintenance Staff'
        MESS = 'mess_staff', 'Mess Staff'
        LAUNDRY = 'laundry_staff', 'Laundry Staff'

    role = models.CharField(max_length=24, choices=Role.choices)
    REQUIRED_FIELDS = ['role']

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=[
                    'student', 'warden', 'chief_warden', 'hostel_director',
                    'maintenance_staff', 'mess_staff', 'laundry_staff',
                ]),
                name='accounts_valid_role',
            ),
        ]


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='student_profile',
    )
    srn = models.CharField(max_length=32, unique=True)
    room = models.CharField(max_length=32, blank=True)
    phone = models.CharField(max_length=24, blank=True)

    def __str__(self):
        return self.srn
