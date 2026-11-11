"""Arin | US-18 Sprint 4. Strict allowlists; all actor/status/snapshot fields server-owned."""
import math
from collections.abc import Mapping
from django.apps import apps
from django.conf import settings
from django.db.models import Sum
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import LeaveRequest, LeaveTransition, AttendanceSession, Attendance, Deviation

class StrictInput(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError({'non_field_errors': ['Expected an object.']})
        unknown = set(data) - set(self.fields)
        if unknown:
            raise PermissionDenied('Protected or unsupported input fields were supplied.')
        return super().to_internal_value(data)

class FiniteFloat(serializers.FloatField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not math.isfinite(value):
            self.fail('invalid')
        return value

class LeaveInput(StrictInput):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(max_length=2000, trim_whitespace=True)
    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError({'end_date': 'Must be on or after start date.'})
        return data

class DecisionInput(StrictInput):
    decision = serializers.ChoiceField(choices=['Approved', 'Rejected', 'Escalated'])
    remarks = serializers.CharField(max_length=2000, trim_whitespace=True)

class TransitionOutput(serializers.ModelSerializer):
    class Meta:
        model = LeaveTransition
        fields = ['id', 'actor', 'from_status', 'to_status', 'remarks', 'occurred_at']

class LeaveOutput(serializers.ModelSerializer):
    transitions = TransitionOutput(many=True, read_only=True)
    class Meta:
        model = LeaveRequest
        fields = ['id', 'student', 'assigned_warden', 'start_date', 'end_date', 'reason', 'status', 'created_at', 'transitions']

class SessionInput(StrictInput):
    title = serializers.CharField(max_length=120)
    opens_at = serializers.DateTimeField()
    closes_at = serializers.DateTimeField()
    centre_latitude = FiniteFloat(min_value=-90, max_value=90)
    centre_longitude = FiniteFloat(min_value=-180, max_value=180)
    radius_m = FiniteFloat(min_value=0.01, max_value=100000)
    max_accuracy_m = FiniteFloat(min_value=0.01, max_value=100000)
    max_sample_age_seconds = serializers.IntegerField(min_value=1, max_value=300)
    def validate(self, data):
        if data['closes_at'] <= data['opens_at']:
            raise serializers.ValidationError({'closes_at': 'Must be later than opening time.'})
        return data

class SessionOutput(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        # No configuration coordinates sent to student UI; policy values are visible.
        fields = ['id', 'title', 'warden', 'opens_at', 'closes_at', 'radius_m', 'max_accuracy_m', 'max_sample_age_seconds']

class AttendanceInput(StrictInput):
    session = serializers.UUIDField()
    latitude = FiniteFloat(min_value=-90, max_value=90)
    longitude = FiniteFloat(min_value=-180, max_value=180)
    accuracy_m = FiniteFloat(min_value=0, max_value=100000)
    sampled_at = serializers.DateTimeField()

class AttendanceOutput(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'session', 'student', 'result', 'reason_code', 'submitted_at']

class DeviationInput(StrictInput):
    student = serializers.CharField(max_length=100)
    rule = serializers.CharField(max_length=100)
    remarks = serializers.CharField(max_length=2000)
    def validate_student(self, value):
        from .permissions import student_key
        return student_key(value)
    def validate_rule(self, value):
        model = apps.get_model(getattr(settings, 'HOSTELSPACE_RULE_MODEL', 'information.Rule'))
        try:
            return model.objects.get(pk=value, active=True)
        except (model.DoesNotExist, ValueError, TypeError):
            raise serializers.ValidationError('Select an active rule.')

class DeactivateInput(StrictInput):
    reason = serializers.CharField(max_length=2000)

class DeviationOutput(serializers.ModelSerializer):
    class Meta:
        model = Deviation
        fields = ['id', 'student', 'rule', 'rule_title_snapshot', 'weightage_snapshot', 'remarks', 'recorded_by', 'recorded_at', 'active', 'deactivated_by', 'deactivated_at', 'deactivation_reason']
