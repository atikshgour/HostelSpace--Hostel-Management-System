from django.urls import path, include
from .health import health
urlpatterns=[path('health/',health),path('api/auth/',include('apps.accounts.urls')),path('api/',include('apps.leave_attendance.urls'))]
