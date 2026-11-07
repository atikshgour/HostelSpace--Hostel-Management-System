from django.urls import path
from . import views

urlpatterns = [
    path("<str:kind>/", views.collection),
    path("<str:kind>/<int:item_id>/", views.detail),
]
