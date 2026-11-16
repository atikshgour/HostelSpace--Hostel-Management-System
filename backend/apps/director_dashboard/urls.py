from django.urls import path

from . import views as v
from .overview import Overview

urlpatterns = [
    path("overview/", Overview.as_view()),
    path("director/users/", v.Users.as_view()),
    path("director/users/<int:pk>/", v.UserDetail.as_view()),
    path("director/settings/", v.Settings.as_view()),
    path("director/summary/", v.Summary.as_view()),
    path("choices/users/", v.Choices.as_view()),
]
