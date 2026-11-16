from django.urls import path
from . import views
urlpatterns = [
    path('leaves/', views.Leaves.as_view()),
    path('leaves/<uuid:pk>/', views.LeaveDetail.as_view()),
    path('leaves/<uuid:pk>/decision/', views.LeaveDecision.as_view()),
    path('attendance/sessions/', views.Sessions.as_view()),
    path('attendance/submit/', views.AttendanceSubmit.as_view()),
    path('attendance/history/', views.AttendanceHistory.as_view()),
    path('deviations/', views.Deviations.as_view()),
    path('deviations/total/', views.DeviationTotals.as_view()),
    path('deviations/<uuid:pk>/deactivate/', views.DeviationDeactivate.as_view()),
    path('arin/students/', views.StudentChoices.as_view()),
    path('arin/rules/', views.RuleChoices.as_view()),
]
