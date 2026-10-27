# Owner: Atiksh | US-20 foundation | Sprint 1
from django.urls import path

from .health import health

urlpatterns = [path('api/health/', health, name='health')]
