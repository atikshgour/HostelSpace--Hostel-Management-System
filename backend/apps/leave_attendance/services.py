"""Arin | US-05/06 Sprint 3; US-07/08 Sprint 4. Authoritative state transitions."""
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from . import permissions as access
from .models import LeaveRequest, LeaveTransition, AttendanceSession, Attendance, Deviation
from .location import check_sample

class Conflict(APIException):
    status_code = 409
    default_detail = 'The record is already in a final or conflicting state.'
    default_code = 'conflict'

@transaction.atomic
def submit_leave(user, data):
    access.require(user, access.STUDENT)
    if data['end_date'] < data['start_date']:
        raise ValidationError({'end_date': 'Must be on or after start date.'})
    record = LeaveRequest.objects.create(student=user, assigned_warden=access.assigned_warden(user), **data)
    LeaveTransition.objects.create(leave=record, actor=user, from_status='', to_status=record.status, remarks='Submitted')
    return record

@transaction.atomic
def decide_leave(user, pk, decision, remarks):
    access.require(user, access.WARDEN, access.CHIEF)
    record = get_object_or_404(access.leave_scope(user, LeaveRequest.objects.all()).select_for_update(), pk=pk)
    old = record.status
    if old in ('Approved', 'Rejected'):
        raise Conflict()
    if old == 'Pending':
        if access.role(user) != access.WARDEN or record.assigned_warden_id != user.pk:
            raise PermissionDenied('Only the assigned warden may decide a Pending request.')
    elif old == 'Escalated':
        if access.role(user) != access.CHIEF or record.assigned_warden.chief_warden_id != user.pk or decision == 'Escalated':
            raise PermissionDenied('Only the supervising Chief Warden may finalize an escalation.')
    if decision not in ('Approved', 'Rejected', 'Escalated'):
        raise ValidationError({'decision': 'Unsupported decision.'})
    record.status = decision
    record.save(update_fields=['status'])
    LeaveTransition.objects.create(leave=record, actor=user, from_status=old, to_status=decision, remarks=remarks)
    return record

def create_session(user, data):
    access.require(user, access.WARDEN)
    return AttendanceSession.objects.create(warden=user, **data)

@transaction.atomic
def submit_attendance(user, session_id, sample):
    access.require(user, access.STUDENT)
    session = get_object_or_404(access.session_scope(user, AttendanceSession.objects.all()), pk=session_id)
    if Attendance.objects.filter(student=user, session=session, result='Accepted').exists():
        raise Conflict('Attendance was already accepted for this session.')
    accepted, reason = check_sample(session, sample, timezone.now())
    try:
        # Nested savepoint keeps the surrounding transaction usable after a uniqueness conflict.
        with transaction.atomic():
            record = Attendance.objects.create(student=user, session=session, result='Accepted' if accepted else 'Rejected', reason_code=reason)
    except IntegrityError:
        if Attendance.objects.filter(student=user, session=session, result='Accepted').exists():
            raise Conflict('Attendance was already accepted for this session.')
        raise
    return record

@transaction.atomic
def record_deviation(user, student_id, rule, remarks):
    access.require(user, access.WARDEN, access.CHIEF)
    student = get_object_or_404(access.students_for(user), pk=student_id)
    # Refresh and lock the rule; snapshot from the server, never from submitted weightage.
    rule = rule.__class__.objects.select_for_update().get(pk=rule.pk)
    if not rule.active or rule.weightage is None or not Decimal('0') <= rule.weightage <= Decimal('99999999.99'):
        raise ValidationError({'rule': 'Select an active rule with a valid nonnegative weightage.'})
    return Deviation.objects.create(student=student, rule=rule, rule_title_snapshot=rule.title, weightage_snapshot=rule.weightage, remarks=remarks, recorded_by=user)

@transaction.atomic
def deactivate_deviation(user, pk, reason):
    access.require(user, access.WARDEN, access.CHIEF)
    record = get_object_or_404(access.personal_scope(user, Deviation.objects.all()).select_for_update(), pk=pk)
    if not record.active:
        raise Conflict('This entry is already inactive; its original history is unchanged.')
    record.active = False
    record.deactivated_by = user
    record.deactivated_at = timezone.now()
    record.deactivation_reason = reason
    record.save(update_fields=['active', 'deactivated_by', 'deactivated_at', 'deactivation_reason'])
    return record
