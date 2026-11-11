from django.urls import path
from . import directory, profile, views

urlpatterns = [
    path("csrf/", views.csrf),
    path("login/", views.login_view),
    path("logout/", views.logout_view),
    path("me/", views.me),
    path("profile/", profile.profile),
    path("users/", directory.users),
    path("users/<int:user_id>/", directory.user_detail),
]
