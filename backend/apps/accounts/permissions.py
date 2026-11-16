# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class ActiveUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_active
        )


def require(user, *roles):
    if not user.is_authenticated or not user.is_active or user.role not in roles:
        raise PermissionDenied("Your role cannot perform this action.")
