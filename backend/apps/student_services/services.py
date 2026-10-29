# Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.accounts.models import StudentProfile, User

from .models import Complaint, ComplaintCategory, ComplaintTransition


@transaction.atomic
def submit_complaint(*, student, category, description):
    # Reload and lock authoritative identity/profile/category state for this write.
    if not User.objects.select_for_update().filter(
        pk=student.pk, is_active=True, role=User.Role.STUDENT,
    ).exists():
        raise PermissionDenied('An active student account is required.')
    profile = StudentProfile.objects.select_for_update().filter(user_id=student.pk).first()
    if profile is None or not profile.room.strip():
        raise ValidationError({'room': ['An assigned profile room is required.']})
    category = ComplaintCategory.objects.select_for_update().filter(
        pk=category.pk, is_active=True,
    ).first()
    if category is None:
        raise ValidationError({'category': ['Select an active complaint category.']})
    if not isinstance(description, str) or not description.strip():
        raise ValidationError({'description': ['Enter a description.']})
    description = description.strip()
    if len(description) > 2000:
        raise ValidationError({'description': ['Use at most 2000 characters.']})
    complaint = Complaint.objects.create(
        student=student, room=profile.room.strip(), category=category,
        description=description, status=Complaint.Status.OPEN,
    )
    ComplaintTransition.objects.create(
        complaint=complaint, actor=student, old_status='',
        new_status=Complaint.Status.OPEN, remarks='Complaint submitted.',
    )
    return complaint


def _remarks(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 500:
        raise ValidationError({'remarks': ['Enter 1–500 characters.']})
    return value.strip()


def _locked_actor(actor, assignee_id=None):
    # Consistent user-before-complaint lock order serializes role/deactivation edits.
    ids = {actor.pk}
    if assignee_id is not None:
        ids.add(assignee_id)
    # NO KEY UPDATE still blocks role changes but permits history FK key-share
    # locks on an assignee held by a concurrent progress transaction.
    users = {u.pk: u for u in User.objects.select_for_update(no_key=True).filter(pk__in=ids).order_by('pk')}
    current = users.get(actor.pk)
    if current is None or not current.is_active or current.role not in (
        User.Role.HOSTEL_DIRECTOR, User.Role.MAINTENANCE,
    ):
        raise PermissionDenied('An active Director or Maintenance Staff account is required.')
    return current, users.get(assignee_id)


def _locked_complaint(actor, complaint_id):
    queryset = Complaint.objects.select_for_update()
    if actor.role != User.Role.HOSTEL_DIRECTOR:
        queryset = queryset.filter(assigned_to_id=actor.pk)
    complaint = queryset.filter(pk=complaint_id).first()
    if complaint is None:
        raise NotFound('Complaint not found.')
    return complaint


@transaction.atomic
def assign_complaint(*, actor, complaint_id, assigned_to, remarks):
    actor, assignee = _locked_actor(actor, assigned_to.pk)
    if actor.role != User.Role.HOSTEL_DIRECTOR:
        raise PermissionDenied('Only the Director can assign complaints.')
    if assignee is None or not assignee.is_active or assignee.role != User.Role.MAINTENANCE:
        raise ValidationError({'assigned_to': ['Select active Maintenance Staff.']})
    remarks = _remarks(remarks)
    complaint = _locked_complaint(actor, complaint_id)
    if complaint.status == Complaint.Status.RESOLVED:
        raise ValidationError({'assigned_to': ['Resolved complaints cannot be reassigned.']})
    if complaint.assigned_to_id == assignee.pk:
        raise ValidationError({'assigned_to': ['This staff member is already assigned.']})
    old_assignee = complaint.assigned_to_id
    complaint.assigned_to = assignee
    complaint.save(update_fields=['assigned_to'])
    ComplaintTransition.objects.create(
        complaint=complaint, actor=actor, old_status=complaint.status,
        new_status=complaint.status, remarks=remarks,
        old_assigned_to_id=old_assignee, new_assigned_to=assignee,
    )
    return complaint


@transaction.atomic
def advance_complaint(*, actor, complaint_id, status, expected_status, remarks):
    actor, _ = _locked_actor(actor)
    remarks = _remarks(remarks)
    complaint = _locked_complaint(actor, complaint_id)
    if complaint.status != expected_status:
        raise ValidationError({'expected_status': ['Complaint changed; reload before retrying.']})
    next_status = {
        Complaint.Status.OPEN: Complaint.Status.IN_PROGRESS,
        Complaint.Status.IN_PROGRESS: Complaint.Status.RESOLVED,
    }.get(complaint.status)
    if status != next_status or next_status is None:
        raise ValidationError({'status': ['Only Open → In Progress → Resolved is permitted.']})
    if complaint.assigned_to_id is None:
        raise ValidationError({'assigned_to': ['Assign Maintenance Staff before starting work.']})
    old_status = complaint.status
    complaint.status = status
    complaint.save(update_fields=['status'])
    ComplaintTransition.objects.create(
        complaint=complaint, actor=actor, old_status=old_status, new_status=status,
        remarks=remarks, old_assigned_to_id=complaint.assigned_to_id,
        new_assigned_to_id=complaint.assigned_to_id,
    )
    return complaint
