from django.urls import path

from . import views as v

urlpatterns = [
    path("information/", v.ContentList.as_view()),
    path("information/<int:pk>/", v.ContentDetail.as_view()),
    path("rules/", v.Rules.as_view()),
    path("rules/<int:pk>/", v.RuleDetail.as_view()),
]
