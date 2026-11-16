from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import AuditEvent, StudentProfile, User
from apps.accounts.services import check_assignments


@transaction.atomic
def save_user(actor, data, obj=None):

    from apps.accounts.permissions import require

    require(actor, "DIRECTOR")
    creating = obj is None
    if creating:
        if not all(data.get(x) for x in ["username", "password", "role"]):
            raise ValidationError("Username, password and role are required.")
        obj = User(managed_by=actor)
    old_role = obj.role
    role = data.get("role", obj.role)
    if not creating and role != old_role:
        if old_role == "STUDENT" or role == "STUDENT":
            raise ValidationError(
                "Student role conversion is not allowed; deactivate and create a separate account to preserve history."
            )
        if obj.wardens.exists() or obj.assigned_students.exists():
            raise ValidationError("Reassign dependent users before changing this role.")
    if not creating and data.get("is_active") is False:
        if obj.pk == actor.pk:
            raise ValidationError("You cannot deactivate your own account.")
        if obj.role == "WARDEN" and obj.assigned_students.exists():
            raise ValidationError("Reassign students before deactivating this warden.")
        if obj.role == "CHIEF_WARDEN" and obj.wardens.filter(is_active=True).exists():
            raise ValidationError(
                "Reassign wardens before deactivating this Chief Warden."
            )
    chief = data.get("chief_warden", obj.chief_warden)
    profile = getattr(obj, "student_profile", None) if obj.pk else None
    warden = data.get("assigned_warden", profile.assigned_warden if profile else None)
    check_assignments(role, chief, warden)
    if (
        role == "CHIEF_WARDEN"
        and data.get("is_active", obj.is_active)
        and User.objects.filter(role=role, is_active=True).exclude(pk=obj.pk).exists()
    ):
        raise ValidationError("Only one active Chief Warden is permitted.")
    if (
        creating
        and role == "STUDENT"
        and not all(data.get(x) for x in ["srn", "room", "assigned_warden"])
    ):
        raise ValidationError("Student SRN, room and assigned warden are required.")
    password = data.get("password")
    for k in [
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "is_active",
        "chief_warden",
    ]:
        if k in data:
            setattr(obj, k, data[k])
    if password:
        try:
            validate_password(password, obj)
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages})
        obj.set_password(password)
    try:
        with transaction.atomic():
            obj.save()
            if role == "STUDENT":
                defaults = {
                    k: data[k]
                    for k in ["srn", "room", "hostel", "assigned_warden"]
                    if k in data
                }
                StudentProfile.objects.update_or_create(user=obj, defaults=defaults)
    except IntegrityError:
        raise ValidationError(
            "Username, SRN or active Chief Warden conflicts with an existing record."
        )
    AuditEvent.objects.create(
        actor=actor,
        action="user_created" if creating else "user_updated",
        object_key=str(obj.pk),
        details={"fields": [k for k in data if k != "password"]},
    )
    return obj
