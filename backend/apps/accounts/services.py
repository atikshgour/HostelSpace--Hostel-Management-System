# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from django.core.validators import RegexValidator
from rest_framework.exceptions import ValidationError

phone_validator = RegexValidator(
    r"^\+?[0-9][0-9 ()-]{6,18}$", "Enter a valid phone number (7–19 characters)."
)


def identity(user):
    p = getattr(user, "student_profile", None)
    return {
        "id": user.pk,
        "username": user.username,
        "name": user.get_full_name() or user.username,
        "role": user.role,
        "email": user.email,
        "profile": (
            {
                "srn": p.srn,
                "hostel": p.hostel,
                "room": p.room,
                "phone": p.phone,
                "assigned_warden": p.assigned_warden_id,
                "warden_name": (
                    p.assigned_warden.get_full_name() or p.assigned_warden.username
                )
                if p.assigned_warden
                else "Not assigned",
            }
            if p
            else None
        ),
    }


def check_assignments(role, chief, warden):
    if chief and (
        role != "WARDEN" or chief.role != "CHIEF_WARDEN" or not chief.is_active
    ):
        raise ValidationError(
            {"chief_warden": "Select an active Chief Warden for a Warden only."}
        )
    if warden and (
        role != "STUDENT" or warden.role != "WARDEN" or not warden.is_active
    ):
        raise ValidationError(
            {"assigned_warden": "Select an active Warden for a Student only."}
        )
