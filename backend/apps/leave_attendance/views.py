"""Arin | US-05–08. Session-only APIs, scoped querysets, bounded pagination, no private-response caching."""
from decimal import Decimal
from django.apps import apps
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from . import permissions as access, services
from .permissions import WorkflowRole
from .models import LeaveRequest, AttendanceSession, Attendance, Deviation
from .serializers import *

class Paging(PageNumberPagination):
    page_size = 25

class ProtectedView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, WorkflowRole]
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'no-store, private'
        response['Vary'] = 'Cookie'
        return response
    def rows(self, queryset, serializer, request):
        pager = Paging()
        return pager.get_paginated_response(serializer(pager.paginate_queryset(queryset, request), many=True).data)
    def validated(self, cls, request):
        s = cls(data=request.data)
        s.is_valid(raise_exception=True)
        return s.validated_data

class Leaves(ProtectedView):
    def get(self, request):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        return self.rows(access.leave_scope(request.user, LeaveRequest.objects.prefetch_related('transitions')).distinct(), LeaveOutput, request)
    def post(self, request):
        access.require(request.user, access.STUDENT)
        return Response(LeaveOutput(services.submit_leave(request.user, self.validated(LeaveInput, request))).data, status=201)

class LeaveDetail(ProtectedView):
    def get(self, request, pk):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        obj = get_object_or_404(access.leave_scope(request.user, LeaveRequest.objects.prefetch_related('transitions')).distinct(), pk=pk)
        return Response(LeaveOutput(obj).data)

class LeaveDecision(ProtectedView):
    def post(self, request, pk):
        access.require(request.user, access.WARDEN, access.CHIEF)
        data = self.validated(DecisionInput, request)
        return Response(LeaveOutput(services.decide_leave(request.user, pk, **data)).data)

class Sessions(ProtectedView):
    def get(self, request):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        return self.rows(access.session_scope(request.user, AttendanceSession.objects.all()), SessionOutput, request)
    def post(self, request):
        access.require(request.user, access.WARDEN)
        return Response(SessionOutput(services.create_session(request.user, self.validated(SessionInput, request))).data, status=201)

class AttendanceSubmit(ProtectedView):
    def post(self, request):
        access.require(request.user, access.STUDENT)
        data = self.validated(AttendanceInput, request)
        session_id = data.pop('session')
        record = services.submit_attendance(request.user, session_id, data)
        return Response(AttendanceOutput(record).data, status=201)

class AttendanceHistory(ProtectedView):
    def get(self, request):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        return self.rows(access.personal_scope(request.user, Attendance.objects.all()), AttendanceOutput, request)

class Deviations(ProtectedView):
    def get(self, request):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        queryset = access.personal_scope(request.user, Deviation.objects.all())
        sid = request.query_params.get('student')
        if sid:
            queryset = queryset.filter(student_id=access.student_key(sid))
        return self.rows(queryset, DeviationOutput, request)
    def post(self, request):
        access.require(request.user, access.WARDEN, access.CHIEF)
        data = self.validated(DeviationInput, request)
        record = services.record_deviation(request.user, data['student'], data['rule'], data['remarks'])
        return Response(DeviationOutput(record).data, status=201)

class DeviationTotals(ProtectedView):
    def get(self, request):
        access.require(request.user, access.STUDENT, access.WARDEN, access.CHIEF)
        if access.role(request.user) == access.STUDENT:
            student = request.user
        else:
            sid = request.query_params.get('student')
            if not sid:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'student': 'Select a student.'})
            student = get_object_or_404(access.students_for(request.user), pk=access.student_key(sid))
        total = Deviation.objects.filter(student=student, active=True).aggregate(value=Sum('weightage_snapshot'))['value'] or Decimal('0')
        return Response({'student': str(student.pk), 'active_total': format(total, '.2f')})

class DeviationDeactivate(ProtectedView):
    def post(self, request, pk):
        access.require(request.user, access.WARDEN, access.CHIEF)
        data = self.validated(DeactivateInput, request)
        return Response(DeviationOutput(services.deactivate_deviation(request.user, pk, data['reason'])).data)

class StudentChoices(ProtectedView):
    def get(self, request):
        access.require(request.user, access.WARDEN, access.CHIEF)
        # Only the necessary identifiers for assigned students, not the shared profile API.
        return self.rows(access.students_for(request.user).order_by('pk'), StudentChoiceOutput, request)

from rest_framework import serializers
class StudentChoiceOutput(serializers.Serializer):
    id = serializers.CharField(source='pk')
    name = serializers.SerializerMethodField()
    def get_name(self, obj):
        return obj.get_full_name() or obj.get_username()

class RuleChoices(ProtectedView):
    def get(self, request):
        access.require(request.user, access.WARDEN, access.CHIEF)
        model = apps.get_model(getattr(settings, 'HOSTELSPACE_RULE_MODEL', 'information.Rule'))
        return self.rows(model.objects.filter(active=True).order_by('pk'), RuleChoiceOutput, request)

class RuleChoiceOutput(serializers.Serializer):
    id = serializers.CharField(source='pk')
    title = serializers.CharField()
    weightage = serializers.DecimalField(max_digits=10, decimal_places=2)
