# Team integration | US-01-20 | Browser -> Next.js -> Django -> PostgreSQL
from django.urls import include, path

from .health import health

urlpatterns = [
    path('health/', health), path('api/health/', health, name='health'),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.student_services.urls')),
    path('api/', include('apps.information.urls')),
    path('api/', include('apps.leave_attendance.urls')),
    path('api/', include('apps.facilities.urls')),
    path('api/', include('apps.director_dashboard.urls')),
]
