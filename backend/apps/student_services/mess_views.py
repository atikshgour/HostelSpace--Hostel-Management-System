# Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User

from .mess_serializers import (
    AllocationSerializer,
    CouponSerializer,
    MessStudentSerializer,
)
from .mess_services import (
    create_allocation,
    create_coupon,
    update_allocation,
    update_coupon,
)
from .models import Coupon, MessAllocation
from .views import ComplaintPagination, StudentAPIView


class IsMessStaff(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.is_active and user.role == User.Role.MESS)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class StudentMess(StudentAPIView):
    def get(self, request):
        today = timezone.localdate(timezone=ZoneInfo('Asia/Kolkata'))
        allocation = MessAllocation.objects.filter(
            student=request.user, is_active=True, valid_from__lte=today, valid_until__gte=today,
        ).first()
        coupons = Coupon.objects.filter(
            allocation=allocation, is_active=True, valid_from__lte=today, valid_until__gte=today,
        ) if allocation else Coupon.objects.none()
        return Response({'as_of': today.isoformat(), 'timezone': 'Asia/Kolkata',
                         'allocation': AllocationSerializer(allocation).data if allocation else None,
                         'coupons': CouponSerializer(coupons, many=True).data})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class MessStaffAPIView(StudentAPIView):
    permission_classes = [IsAuthenticated, IsMessStaff]
    pagination_class = ComplaintPagination


class MessStudentList(MessStaffAPIView, generics.ListAPIView):
    serializer_class = MessStudentSerializer
    queryset = User.objects.filter(is_active=True, role=User.Role.STUDENT).order_by('username', 'pk')


class AllocationList(MessStaffAPIView, generics.ListAPIView):
    serializer_class = AllocationSerializer
    queryset = MessAllocation.objects.all()

    def post(self, request):
        record = create_allocation(actor=request.user, data=request.data)
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)


class AllocationDetail(MessStaffAPIView, generics.RetrieveAPIView):
    serializer_class = AllocationSerializer
    queryset = MessAllocation.objects.all()

    def patch(self, request, pk):
        record = update_allocation(actor=request.user, pk=pk, data=request.data)
        return Response(self.get_serializer(record).data)


class CouponList(MessStaffAPIView, generics.ListAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()

    def post(self, request):
        record = create_coupon(actor=request.user, data=request.data)
        return Response(self.get_serializer(record).data, status=status.HTTP_201_CREATED)


class CouponDetail(MessStaffAPIView, generics.RetrieveAPIView):
    serializer_class = CouponSerializer
    queryset = Coupon.objects.all()

    def patch(self, request, pk):
        record = update_coupon(actor=request.user, pk=pk, data=request.data)
        return Response(self.get_serializer(record).data)
