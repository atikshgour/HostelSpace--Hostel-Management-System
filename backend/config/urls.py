# Owner: Atiksh Gour | US-13-16/20 | Shared auth integration
from django.urls import include, path

from apps.accounts.views import UserChoices

from .health import health

urlpatterns = [
    path("api/choices/users/", UserChoices.as_view()),
    path("health/", health),
    path("api/health/", health, name="health"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.student_services.urls")),
]
