# Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User

from .authentication import StudentSessionAuthentication
from .models import Complaint
from .permissions import IsActiveStudent, IsComplaintStaff, IsDirector
from .queries import active_categories, own_complaints
from .serializers import (
    ComplaintAssignmentSerializer,
    ComplaintCategorySerializer,
    ComplaintProgressSerializer,
    ComplaintSerializer,
    ComplaintSubmissionSerializer,
    MaintenanceStaffSerializer,
)
from .services import advance_complaint, assign_complaint, submit_complaint


class ComplaintPagination(PageNumberPagination):
    page_size = 20


@method_decorator(never_cache, name='dispatch')
class StudentAPIView(generics.GenericAPIView):
    authentication_classes = [StudentSessionAuthentication]
    permission_classes = [IsAuthenticated, IsActiveStudent]


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ComplaintCategoryList(StudentAPIView, generics.ListAPIView):
    serializer_class = ComplaintCategorySerializer
    pagination_class = ComplaintPagination

    def get_queryset(self):
        return active_categories()


class ComplaintListCreate(StudentAPIView, generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer
    pagination_class = ComplaintPagination

    def get_queryset(self):
        return own_complaints(self.request.user)

    def create(self, request, *args, **kwargs):
        submission = ComplaintSubmissionSerializer(data=request.data)
        submission.is_valid(raise_exception=True)
        complaint = submit_complaint(student=request.user, **submission.validated_data)
        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)


class ComplaintDetail(StudentAPIView, generics.RetrieveAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return own_complaints(self.request.user)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ComplaintStaffList(StudentAPIView, generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsComplaintStaff]
    serializer_class = ComplaintSerializer
    pagination_class = ComplaintPagination

    def get_queryset(self):
        queryset = Complaint.objects.select_related('category').prefetch_related('history')
        if self.request.user.role != User.Role.HOSTEL_DIRECTOR:
            queryset = queryset.filter(assigned_to=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['can_assign'] = request.user.role == User.Role.HOSTEL_DIRECTOR
        return response


class MaintenanceStaffList(StudentAPIView, generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsDirector]
    serializer_class = MaintenanceStaffSerializer
    pagination_class = ComplaintPagination
    queryset = User.objects.filter(is_active=True, role=User.Role.MAINTENANCE).order_by('username', 'pk')


class ComplaintAssignment(StudentAPIView):
    permission_classes = [IsAuthenticated, IsDirector]

    def post(self, request, pk):
        serializer = ComplaintAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint = assign_complaint(actor=request.user, complaint_id=pk, **serializer.validated_data)
        return Response(ComplaintSerializer(complaint).data)


class ComplaintProgress(StudentAPIView):
    permission_classes = [IsAuthenticated, IsComplaintStaff]

    def post(self, request, pk):
        serializer = ComplaintProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        complaint = advance_complaint(actor=request.user, complaint_id=pk, **serializer.validated_data)
        return Response(ComplaintSerializer(complaint).data)
