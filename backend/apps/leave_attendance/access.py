"""Arin | US-18/22. Integration boundary with Anvi's shared accounts model.
Contract: user.role; user.student_profile.assigned_warden; warden.chief_warden_id.
Do not add a second user model to the production repository.
"""
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError

STUDENT = 'STUDENT'
WARDEN = 'WARDEN'
CHIEF = 'CHIEF_WARDEN'

def role(user):
    return getattr(user, 'role', '') if user.is_authenticated and user.is_active else ''

def require(user, *allowed):
    if role(user) not in allowed:
        raise PermissionDenied('Your role cannot perform this action.')

def students_for(user):
    users = get_user_model().objects.filter(role=STUDENT, is_active=True)
    if role(user) == WARDEN:
        return users.filter(student_profile__assigned_warden=user)
    if role(user) == CHIEF:
        return users.filter(student_profile__assigned_warden__chief_warden=user)
    return users.none()

def assigned_warden(student):
    profile = getattr(student, 'student_profile', None)
    warden = getattr(profile, 'assigned_warden', None)
    if warden is None or not warden.is_active or role(warden) != WARDEN:
        raise ValidationError({'assigned_warden': 'An active warden must be assigned before submission.'})
    return warden

def leave_scope(user, queryset):
    if role(user) == STUDENT:
        return queryset.filter(student=user)
    if role(user) == WARDEN:
        return queryset.filter(assigned_warden=user)
    if role(user) == CHIEF:
        from .models import LeaveTransition
        return queryset.filter(assigned_warden__chief_warden=user).filter(Q(status='Escalated') | Q(pk__in=LeaveTransition.objects.filter(actor=user).values('leave_id')))
    return queryset.none()

def personal_scope(user, queryset):
    if role(user) == STUDENT:
        return queryset.filter(student=user)
    if role(user) in (WARDEN, CHIEF):
        return queryset.filter(student__in=students_for(user))
    return queryset.none()

def session_scope(user, queryset):
    if role(user) == STUDENT:
        profile = getattr(user, 'student_profile', None)
        return queryset.filter(warden_id=getattr(profile, 'assigned_warden_id', None))
    if role(user) == WARDEN:
        return queryset.filter(warden=user)
    if role(user) == CHIEF:
        return queryset.filter(warden__chief_warden=user)
    return queryset.none()


def student_key(value):
    """Validate IDs against the actual configured user primary key, not an assumed int."""
    from django.core.exceptions import ValidationError as DjangoValidationError
    try:
        return get_user_model()._meta.pk.to_python(value)
    except (DjangoValidationError, ValueError, TypeError):
        raise ValidationError({'student': 'Select a valid student identifier.'})
