"""Arin Singh | US-05–08, US-18, US-22.

The shared accounts app owns users and assignments. This module is the single
adapter between that contract and Arin's workflows; it deliberately does not
introduce another user model.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import BasePermission

STUDENT = "STUDENT"
WARDEN = "WARDEN"
CHIEF = "CHIEF_WARDEN"

def role(user):
    if not getattr(user, "is_authenticated", False) or not user.is_active:
        return ""
    return getattr(user, "role", "")

def require(user, *allowed):
    if role(user) not in allowed:
        raise PermissionDenied("Your role cannot perform this action.")

def students_for(user):
    users = get_user_model().objects.filter(role=STUDENT, is_active=True)
    if role(user) == WARDEN:
        return users.filter(student_profile__assigned_warden=user)
    if role(user) == CHIEF:
        return users.filter(student_profile__assigned_warden__chief_warden=user)
    return users.none()

def assigned_warden(student):
    profile = getattr(student, "student_profile", None)
    warden = getattr(profile, "assigned_warden", None)
    if warden is None or not warden.is_active or role(warden) != WARDEN:
        raise ValidationError({"assigned_warden": "An active warden must be assigned before submission."})
    return warden

def leave_scope(user, queryset):
    if role(user) == STUDENT:
        return queryset.filter(student=user)
    if role(user) == WARDEN:
        return queryset.filter(assigned_warden=user)
    if role(user) == CHIEF:
        from .models import LeaveTransition
        finalized = LeaveTransition.objects.filter(actor=user).values("leave_id")
        return queryset.filter(assigned_warden__chief_warden=user).filter(Q(status="Escalated") | Q(pk__in=finalized))
    return queryset.none()

def personal_scope(user, queryset):
    if role(user) == STUDENT:
        return queryset.filter(student=user)
    if role(user) in (WARDEN, CHIEF):
        return queryset.filter(student__in=students_for(user))
    return queryset.none()

def session_scope(user, queryset):
    if role(user) == STUDENT:
        profile = getattr(user, "student_profile", None)
        return queryset.filter(warden_id=getattr(profile, "assigned_warden_id", None))
    if role(user) == WARDEN:
        return queryset.filter(warden=user)
    if role(user) == CHIEF:
        return queryset.filter(warden__chief_warden=user)
    return queryset.none()

def student_key(value):
    try:
        return get_user_model()._meta.pk.to_python(value)
    except (DjangoValidationError, ValueError, TypeError):
        raise ValidationError({"student": "Select a valid student identifier."})

class WorkflowRole(BasePermission):
    """Coarse role gate; every record endpoint also applies a scoped query."""
    def has_permission(self, request, view):
        return role(request.user) in (STUDENT, WARDEN, CHIEF)
