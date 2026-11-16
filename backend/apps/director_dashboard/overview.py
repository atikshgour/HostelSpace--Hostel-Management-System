from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.serializers import ProtectedView
from apps.facilities.models import LaundryRecord, StudyRoom
from apps.facilities.services import schedule
from apps.information.models import Content
from apps.leave_attendance.models import LeaveRequest
from apps.student_services.models import Complaint, FeeDue, MessAllocation


class Overview(ProtectedView):
    def get(self, request):
        u = request.user
        now = timezone.now()
        students = User.objects.filter(role="STUDENT", is_active=True)
        if u.role == "STUDENT":
            students = students.filter(pk=u.pk)
        elif u.role == "WARDEN":
            students = students.filter(student_profile__assigned_warden=u)
        elif u.role == "CHIEF_WARDEN":
            students = students.filter(student_profile__assigned_warden__chief_warden=u)
        elif u.role not in ("DIRECTOR", "LAUNDRY_STAFF", "MESS_STAFF"):
            students = students.none()
        leaves = LeaveRequest.objects.filter(student__in=students)
        complaints = Complaint.objects.filter(student__in=students)
        if u.role == "MAINTENANCE_STAFF":
            complaints = Complaint.objects.filter(assigned_to=u)
        laundry = LaundryRecord.objects.filter(student__in=students)
        notices = (
            Content.objects.filter(kind="notice", active=True)
            .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
            .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
            .order_by("-pk")[:3]
        )
        result = {
            "active_students": students.count(),
            "pending_leave": leaves.filter(status="Pending").count(),
            "open_complaints": complaints.exclude(status="Resolved").count(),
            "unpaid_fees": FeeDue.objects.filter(
                student__in=students, status="Unpaid"
            ).count(),
            "laundry_received": laundry.filter(status="Received").count(),
            "laundry_ready": laundry.filter(status="Ready").count(),
            "study_room": getattr(StudyRoom.objects.first(), "status", "Closed"),
        }
        # Published notices are available to every signed-in resident; never include private operational rows.
        result["notices"] = [
            {"id": n.pk, "title": n.title, "body": n.body} for n in notices
        ]
        if u.role == "STUDENT":
            result["laundry"] = schedule(u)
            result["mess"] = getattr(
                MessAllocation.objects.filter(student=u).first(),
                "mess_name",
                "Not assigned",
            )
        if u.role == "LAUNDRY_STAFF":
            result = {
                k: v
                for k, v in result.items()
                if k
                in (
                    "active_students",
                    "laundry_received",
                    "laundry_ready",
                    "notices",
                    "study_room",
                )
            }
        if u.role == "MESS_STAFF":
            result = {
                k: v
                for k, v in result.items()
                if k in ("active_students", "notices", "study_room")
            }
        if u.role == "MAINTENANCE_STAFF":
            result = {
                k: v
                for k, v in result.items()
                if k in ("open_complaints", "notices", "study_room")
            }
        if u.role == "CONTENT_STAFF":
            result = {k: v for k, v in result.items() if k in ("notices", "study_room")}
        if u.role in ("WARDEN", "CHIEF_WARDEN"):
            result = {
                k: v
                for k, v in result.items()
                if k in ("active_students", "pending_leave", "notices", "study_room")
            }
        return Response(result)
