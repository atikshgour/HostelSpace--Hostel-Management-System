# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from django.urls import path

from .views import ComplaintCategoryList, ComplaintDetail, ComplaintListCreate

urlpatterns = [
    path('complaint-categories/', ComplaintCategoryList.as_view(), name='complaint-categories'),
    path('complaints/', ComplaintListCreate.as_view(), name='complaint-list'),
    path('complaints/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
]
