"""Arin | US-18. Director summaries call these read-only aggregates after Director authorization."""
from .models import LeaveRequest, Attendance

def pending_leave_count():
    return LeaveRequest.objects.filter(status='Pending').count()

def accepted_attendance_count(session_id):
    return Attendance.objects.filter(session_id=session_id, result='Accepted').count()
