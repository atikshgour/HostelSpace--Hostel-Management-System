# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .permissions import require
from .serializers import ProtectedView, StrictSerializer
from .services import identity, phone_validator


class LoginInput(StrictSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=256, trim_whitespace=False)


class ProfileInput(StrictSerializer):
    phone = serializers.CharField(max_length=20, validators=[phone_validator])


class LoginThrottle(AnonRateThrottle):
    scope = "login"
    rate = "10/min"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class Csrf(ProtectedView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class Login(ProtectedView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        s = self.validate(LoginInput, request)
        user = authenticate(request, **s.validated_data)
        if user is None or not user.is_active:
            return Response(
                {
                    "code": "invalid_credentials",
                    "message": "Invalid username or password.",
                    "fields": {},
                },
                status=400,
            )
        login(request, user)
        return Response(identity(user))


class Logout(ProtectedView):
    def post(self, request):
        logout(request)
        return Response({"message": "Signed out."})


class Me(ProtectedView):
    def get(self, request):
        return Response(identity(request.user))


class Profile(ProtectedView):
    def get(self, request):
        require(request.user, "STUDENT")
        return Response(identity(request.user))

    def patch(self, request):
        require(request.user, "STUDENT")
        s = self.validate(ProfileInput, request)
        p = request.user.student_profile
        p.phone = s.validated_data["phone"]
        p.save(update_fields=["phone"])
        return Response(identity(request.user))


class UserChoices(ProtectedView):
    def get(self, request):
        from .models import User

        require(request.user, "DIRECTOR", "WARDEN", "MESS_STAFF")
        role = request.query_params.get("role", "STUDENT")
        if role not in ("STUDENT", "MAINTENANCE_STAFF"):
            raise serializers.ValidationError(
                {"role": "Select STUDENT or MAINTENANCE_STAFF."}
            )
        users = User.objects.filter(is_active=True, role=role).order_by("pk")
        if role == "STUDENT" and request.user.role == "WARDEN":
            users = users.filter(student_profile__assigned_warden=request.user)
        if role == "MAINTENANCE_STAFF":
            require(request.user, "DIRECTOR", "WARDEN")
        return Response(
            {
                "results": [
                    {"id": u.pk, "name": u.get_full_name() or u.username} for u in users
                ]
            }
        )
