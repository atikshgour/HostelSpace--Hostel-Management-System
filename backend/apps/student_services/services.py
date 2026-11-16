# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import AuditEvent
from apps.accounts.permissions import require

from .models import Complaint, ComplaintTransition


@transaction.atomic
def submit_complaint(user, data):
    require(user, "STUDENT")
    p = getattr(user, "student_profile", None)
    if not p:
        raise ValidationError({"profile": "A student room profile is required."})
    obj = Complaint.objects.create(
        student=user, room_snapshot=f"{p.hostel} / {p.room}", **data
    )
    ComplaintTransition.objects.create(
        complaint=obj, actor=user, to_status="Open", remarks="Submitted"
    )
    return obj


@transaction.atomic
def progress(user, pk, status, remarks):
    require(user, "DIRECTOR", "MAINTENANCE_STAFF")
    obj = get_object_or_404(Complaint.objects.select_for_update(), pk=pk)
    if user.role != "DIRECTOR" and obj.assigned_to_id != user.pk:
        raise PermissionDenied(
            "Only assigned maintenance staff may update this complaint."
        )
    if not obj.assigned_to_id:
        raise ValidationError(
            {"assigned_to": "Assign maintenance staff before progressing."}
        )
    allowed = {"Open": "In Progress", "In Progress": "Resolved"}
    if allowed.get(obj.status) != status:
        raise ValidationError(
            {"status": "Only Open → In Progress → Resolved is allowed."}
        )
    old = obj.status
    obj.status = status
    obj.save(update_fields=["status"])
    ComplaintTransition.objects.create(
        complaint=obj, actor=user, from_status=old, to_status=status, remarks=remarks
    )
    return obj


@transaction.atomic
def select_mess(actor, option, student=None):
    from apps.accounts.models import User

    from .models import MessAllocation, MessChoiceEvent, MessOption

    require(actor, "MESS_STAFF")
    if student is None or student.role != "STUDENT" or not student.is_active:
        raise ValidationError({"student": "Select an active student."})
    User.objects.select_for_update().get(pk=student.pk)
    option = MessOption.objects.select_for_update().get(pk=option.pk)
    current = MessAllocation.objects.filter(student=student).first()
    if not option.active:
        raise ValidationError({"option": "This mess is not accepting allocations."})
    if current and current.option_id == option.pk:
        return current
    if option.allocations.filter(student__is_active=True).count() >= option.capacity:
        raise ValidationError({"option": "This mess is full."})
    old = current.mess_name if current else ""
    obj, _ = MessAllocation.objects.update_or_create(
        student=student,
        defaults={"option": option, "mess_name": option.name, "assigned_by": actor},
    )
    MessChoiceEvent.objects.create(
        student=student, actor=actor, old_mess=old, new_mess=option.name
    )
    AuditEvent.objects.create(
        actor=actor,
        action="mess_selected",
        object_key=str(student.pk),
        details={"from": old, "to": option.name},
    )
    return obj
