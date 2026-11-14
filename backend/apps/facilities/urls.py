from django.urls import path
from . import views as v
urlpatterns=[path('laundry/policy/',v.Policy.as_view()),path('laundry/records/<int:pk>/ready/',v.Ready.as_view()),path('study-room/',v.Study.as_view()),path('laundry/allocations/',v.Allocations.as_view()),path('laundry/records/',v.Records.as_view()),path('laundry/records/<int:pk>/collect/',v.Collect.as_view())]
