"""Arin Singh | US-05/06 Sprint 3; US-07/08 Sprint 4. Server-owned audit data."""
import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q, F

class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending'
        ESCALATED = 'Escalated'
        APPROVED = 'Approved'
        REJECTED = 'Rejected'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_leaves')
    assigned_warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_assigned_leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=2000)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at', '-id']
        constraints = [models.CheckConstraint(condition=Q(end_date__gte=F('start_date')), name='arin_leave_valid_dates')]

class LeaveTransition(models.Model):
    leave = models.ForeignKey(LeaveRequest, on_delete=models.PROTECT, related_name='transitions')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    from_status = models.CharField(max_length=12, blank=True)
    to_status = models.CharField(max_length=12)
    remarks = models.TextField(max_length=2000, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['occurred_at', 'id']

class AttendanceSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120)
    warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_sessions')
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    centre_latitude = models.FloatField()
    centre_longitude = models.FloatField()
    radius_m = models.FloatField()
    max_accuracy_m = models.FloatField()
    max_sample_age_seconds = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-opens_at', '-id']
        constraints = [
            models.CheckConstraint(condition=Q(closes_at__gt=F('opens_at')), name='arin_session_valid_window'),
            models.CheckConstraint(condition=Q(radius_m__gt=0), name='arin_session_positive_radius'),
            models.CheckConstraint(condition=Q(max_accuracy_m__gt=0), name='arin_session_positive_accuracy'),
            models.CheckConstraint(condition=Q(max_sample_age_seconds__gt=0), name='arin_session_positive_age'),
            models.CheckConstraint(condition=Q(centre_latitude__gte=-90, centre_latitude__lte=90), name='arin_session_latitude'),
            models.CheckConstraint(condition=Q(centre_longitude__gte=-180, centre_longitude__lte=180), name='arin_session_longitude'),
        ]

class Attendance(models.Model):
    class Result(models.TextChoices):
        ACCEPTED = 'Accepted'
        REJECTED = 'Rejected'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AttendanceSession, on_delete=models.PROTECT, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_attendance')
    result = models.CharField(max_length=8, choices=Result.choices)
    reason_code = models.CharField(max_length=40)
    submitted_at = models.DateTimeField(auto_now_add=True)
    # No student latitude, longitude, accuracy, or distance field: discard the sample after checking.
    class Meta:
        ordering = ['-submitted_at', '-id']
        constraints = [models.UniqueConstraint(fields=['session', 'student'], condition=Q(result='Accepted'), name='arin_one_accepted_per_session')]

class Deviation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_deviations')
    rule = models.ForeignKey(getattr(settings, 'HOSTELSPACE_RULE_MODEL', 'information.Rule'), on_delete=models.PROTECT)
    rule_title_snapshot = models.CharField(max_length=200)
    weightage_snapshot = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(max_length=2000)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='arin_recorded_deviations')
    recorded_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    deactivated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='arin_deactivated_deviations')
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivation_reason = models.TextField(max_length=2000, blank=True)
    class Meta:
        ordering = ['-recorded_at', '-id']
        constraints = [models.CheckConstraint(condition=Q(weightage_snapshot__gte=0), name='arin_nonnegative_weightage')]
