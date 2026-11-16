from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from apps.accounts.models import AuditEvent, SiteSetting, User
from apps.accounts.permissions import require
from apps.accounts.serializers import ProtectedView
from apps.accounts.services import identity
from apps.leave_attendance.models import AttendanceSession, LeaveRequest
from apps.student_services.models import Complaint, FeeDue

from .serializers import SettingInput, UserInput
from .services import save_user


class Users(ProtectedView):
    def get(self, request):
        require(request.user, "DIRECTOR")
        q = User.objects.select_related("student_profile", "managed_by").order_by("pk")
        if request.user.role == "WARDEN":
            q = q.filter(
                Q(student_profile__assigned_warden=request.user)
                | Q(managed_by=request.user)
            ).exclude(role__in=["DIRECTOR", "WARDEN", "CHIEF_WARDEN"])
        return Response(
            {
                "results": [
                    dict(
                        identity(u),
                        first_name=u.first_name,
                        last_name=u.last_name,
                        is_active=u.is_active,
                        chief_warden=u.chief_warden_id,
                    )
                    for u in q
                ]
            }
        )

    def post(self, request):
        require(request.user, "DIRECTOR")
        s = self.validate(UserInput, request)
        return Response(identity(save_user(request.user, s.validated_data)), status=201)


class UserDetail(ProtectedView):
    @transaction.atomic
    def patch(self, request, pk):
        require(request.user, "DIRECTOR")
        s = self.validate(UserInput, request)
        u = get_object_or_404(User.objects.select_for_update(), pk=pk)
        u = save_user(request.user, s.validated_data, u)
        return Response(dict(identity(u), is_active=u.is_active))


class Settings(ProtectedView):
    def get(self, request):
        require(request.user, "DIRECTOR")
        return Response(
            {
                "results": list(
                    SiteSetting.objects.order_by("key").values(
                        "key", "value", "updated_at"
                    )
                )
            }
        )

    def post(self, request):
        require(request.user, "DIRECTOR")
        s = self.validate(SettingInput, request)
        obj, _ = SiteSetting.objects.update_or_create(
            key=s.validated_data["key"],
            defaults={"value": s.validated_data["value"], "updated_by": request.user},
        )
        AuditEvent.objects.create(
            actor=request.user,
            action="setting_updated",
            object_key=obj.key,
            details={"value": obj.value},
        )
        return Response({"key": obj.key, "value": obj.value})


class Summary(ProtectedView):
    def get(self, request):
        require(request.user, "DIRECTOR")
        sessions = AttendanceSession.objects.annotate(
            accepted=Count("submissions", filter=Q(submissions__result="Accepted"))
        ).order_by("-opens_at")
        return Response(
            {
                "pending_leave": LeaveRequest.objects.filter(status="Pending").count(),
                "escalated_leave": LeaveRequest.objects.filter(
                    status="Escalated"
                ).count(),
                "open_complaints": Complaint.objects.exclude(status="Resolved").count(),
                "unpaid_fees": FeeDue.objects.filter(status="Unpaid").count(),
                "active_students": User.objects.filter(
                    role="STUDENT", is_active=True
                ).count(),
                "attendance_by_session": list(
                    sessions.values("id", "title", "opens_at", "accepted")[:100]
                ),
            }
        )


class Choices(ProtectedView):
    def get(self, request):
        require(
            request.user,
            "DIRECTOR",
            "WARDEN",
            "LAUNDRY_STAFF",
            "MESS_STAFF",
            "CONTENT_STAFF",
        )
        role = request.query_params.get("role", "STUDENT")
        if role not in User.Role.values:
            return Response({"results": []})
        if request.user.role not in ("DIRECTOR", "WARDEN") and role != "STUDENT":
            require(request.user, "DIRECTOR")
        q = User.objects.filter(role=role, is_active=True)
        if request.user.role == "WARDEN" and role == "STUDENT":
            q = q.filter(student_profile__assigned_warden=request.user)
        if request.user.role == "WARDEN" and role not in (
            "STUDENT",
            "LAUNDRY_STAFF",
            "MESS_STAFF",
            "MAINTENANCE_STAFF",
            "CONTENT_STAFF",
        ):
            q = q.none()
        return Response(
            {
                "results": [
                    {
                        "id": u.pk,
                        "name": u.get_full_name() or u.username,
                        "role": u.role,
                    }
                    for u in q.order_by("pk")
                ]
            }
        )
