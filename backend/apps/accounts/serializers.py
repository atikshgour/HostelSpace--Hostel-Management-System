# Owner: Anvi Srinivas | US-01,US-02 | Dev sprint 1; 2 | SRS sprint 1 | Reviewer: Arin Singh (pending)
from collections.abc import Mapping

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView

from .permissions import ActiveUser


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError("Expected a JSON object.")
        unknown = set(data) - set(self.fields)
        if unknown:
            raise PermissionDenied(
                "Unsupported or protected fields: " + ", ".join(sorted(unknown))
            )
        return super().to_internal_value(data)


class StrictModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            raise serializers.ValidationError("Expected a JSON object.")
        unknown = set(data) - {k for k, v in self.fields.items() if not v.read_only}
        if unknown:
            raise PermissionDenied(
                "Unsupported or protected fields: " + ", ".join(sorted(unknown))
            )
        return super().to_internal_value(data)


class ProtectedView(APIView):
    permission_classes = [ActiveUser]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store, private"
        response["Vary"] = "Cookie"
        return response

    def validate(self, cls, request, **kwargs):
        s = cls(data=request.data, **kwargs)
        s.is_valid(raise_exception=True)
        return s

    def rows(self, queryset, serializer, request):
        from rest_framework.pagination import PageNumberPagination

        pager = PageNumberPagination()
        pager.page_size = 50
        return pager.get_paginated_response(
            serializer(pager.paginate_queryset(queryset, request), many=True).data
        )
