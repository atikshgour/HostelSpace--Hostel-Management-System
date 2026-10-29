# Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
from django.urls import path

from .mess_views import (
    AllocationDetail,
    AllocationList,
    CouponDetail,
    CouponList,
    MessStudentList,
    StudentMess,
)
from .views import (
    ComplaintAssignment,
    ComplaintCategoryList,
    ComplaintDetail,
    ComplaintListCreate,
    ComplaintProgress,
    ComplaintStaffList,
    MaintenanceStaffList,
)

urlpatterns = [
    path('mess/', StudentMess.as_view(), name='student-mess'),
    path('mess/students/', MessStudentList.as_view(), name='mess-students'),
    path('mess/allocations/', AllocationList.as_view(), name='mess-allocations'),
    path('mess/allocations/<int:pk>/', AllocationDetail.as_view(), name='mess-allocation-detail'),
    path('mess/coupons/', CouponList.as_view(), name='mess-coupons'),
    path('mess/coupons/<int:pk>/', CouponDetail.as_view(), name='mess-coupon-detail'),
    path('complaint-categories/', ComplaintCategoryList.as_view(), name='complaint-categories'),
    path('complaints/', ComplaintListCreate.as_view(), name='complaint-list'),
    path('complaints/manage/', ComplaintStaffList.as_view(), name='complaint-manage'),
    path('maintenance-staff/', MaintenanceStaffList.as_view(), name='maintenance-staff'),
    path('complaints/<int:pk>/assign/', ComplaintAssignment.as_view(), name='complaint-assign'),
    path('complaints/<int:pk>/progress/', ComplaintProgress.as_view(), name='complaint-progress'),
    path('complaints/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
]
