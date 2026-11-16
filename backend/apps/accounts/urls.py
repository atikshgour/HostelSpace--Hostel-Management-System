# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.Csrf.as_view()),
    path("login/", views.Login.as_view()),
    path("logout/", views.Logout.as_view()),
    path("me/", views.Me.as_view()),
    path("profile/", views.Profile.as_view()),
]
