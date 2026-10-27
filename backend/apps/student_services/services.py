# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError

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
