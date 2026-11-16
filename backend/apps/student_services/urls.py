# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
from django.urls import path

from . import views as v

urlpatterns = [
    path("mess/options/", v.MessOptions.as_view()),
    path("mess/options/<int:pk>/", v.MessOptionDetail.as_view()),
    path("mess/select/", v.MessSelect.as_view()),
    path("mess/history/", v.MessHistory.as_view()),
    path("complaints/", v.Complaints.as_view()),
    path("complaints/<int:pk>/", v.ComplaintDetail.as_view()),
    path("complaints/<int:pk>/assign/", v.ComplaintAssign.as_view()),
    path("complaints/<int:pk>/progress/", v.ComplaintProgress.as_view()),
    path("mess/", v.Mess.as_view()),
    path("mess/coupons/", v.Coupons.as_view()),
    path("mess/coupons/<int:pk>/", v.CouponDetail.as_view()),
    path("fees/", v.Fees.as_view()),
    path("payments/attempts/", v.Attempts.as_view()),
    path("payments/initiate/", v.Initiate.as_view()),
    path("payments/verify/", v.Verify.as_view()),
    path("payments/simulate/", v.Simulate.as_view()),
]
