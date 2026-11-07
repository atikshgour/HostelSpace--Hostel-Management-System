from django.urls import include, path
from .views import health

urlpatterns = [
    path("api/health/", health),
    path("api/auth/", include("accounts.urls")),
      path("api/content/", include("content.urls")),
]
