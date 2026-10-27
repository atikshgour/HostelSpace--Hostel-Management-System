# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authentication import StudentSessionAuthentication
from .permissions import IsActiveStudent
from .queries import active_categories, own_complaints
from .serializers import (
    ComplaintCategorySerializer,
    ComplaintSerializer,
    ComplaintSubmissionSerializer,
)
from .services import submit_complaint


class ComplaintPagination(PageNumberPagination):
    page_size = 20


@method_decorator(never_cache, name='dispatch')
class StudentAPIView(generics.GenericAPIView):
    authentication_classes = [StudentSessionAuthentication]
    permission_classes = [IsAuthenticated, IsActiveStudent]


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ComplaintCategoryList(StudentAPIView, generics.ListAPIView):
    serializer_class = ComplaintCategorySerializer
    pagination_class = ComplaintPagination

    def get_queryset(self):
        return active_categories()


class ComplaintListCreate(StudentAPIView, generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer
    pagination_class = ComplaintPagination

    def get_queryset(self):
        return own_complaints(self.request.user)

    def create(self, request, *args, **kwargs):
        submission = ComplaintSubmissionSerializer(data=request.data)
        submission.is_valid(raise_exception=True)
        complaint = submit_complaint(student=request.user, **submission.validated_data)
        return Response(ComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)


class ComplaintDetail(StudentAPIView, generics.RetrieveAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return own_complaints(self.request.user)
