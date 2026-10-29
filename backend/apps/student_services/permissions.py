# Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsActiveStudent(BasePermission):
    message = 'An active student account is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and user.role == User.Role.STUDENT)


class IsComplaintStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and user.role in (
            User.Role.HOSTEL_DIRECTOR, User.Role.MAINTENANCE,
        ))


class IsDirector(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and user.role == User.Role.HOSTEL_DIRECTOR)
