# Owner: Atiksh Gour | US-13/14 | Sprint 4 | Reviewer: Anvi Srinivas
from django.urls import path

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
    path('complaint-categories/', ComplaintCategoryList.as_view(), name='complaint-categories'),
    path('complaints/', ComplaintListCreate.as_view(), name='complaint-list'),
    path('complaints/manage/', ComplaintStaffList.as_view(), name='complaint-manage'),
    path('maintenance-staff/', MaintenanceStaffList.as_view(), name='maintenance-staff'),
    path('complaints/<int:pk>/assign/', ComplaintAssignment.as_view(), name='complaint-assign'),
    path('complaints/<int:pk>/progress/', ComplaintProgress.as_view(), name='complaint-progress'),
    path('complaints/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
]
