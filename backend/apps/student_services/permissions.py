# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from rest_framework.permissions import BasePermission

from apps.accounts.models import User


class IsActiveStudent(BasePermission):
    message = 'An active student account is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and user.role == User.Role.STUDENT)
