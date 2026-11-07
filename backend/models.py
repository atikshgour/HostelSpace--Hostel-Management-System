# Owner: Anvi Srinivas | Story: US-01 | Sprint: 1
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    STUDENT = "student", "Student"
    WARDEN = "warden", "Warden"
    CHIEF_WARDEN = "chief_warden", "Chief Warden"
    DIRECTOR = "director", "Hostel Director"
    MAINTENANCE = "maintenance", "Maintenance Staff"
    MESS = "mess", "Mess Staff"
    LAUNDRY = "laundry", "Laundry Staff"


class User(AbstractUser):
    """Single shared user model for all roles."""
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=15, blank=True)
    usn = models.CharField(max_length=20, blank=True)
    room_number = models.CharField(max_length=10, blank=True)
