# Owner: Arin Singh | US-18 | Dev sprint 1 | SRS sprint 1 | Reviewer: Aryan Singh (pending)
"""Shared DRF error envelope for HostelSpace APIs."""

from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        response = Response(
            {
                "code": "conflict",
                "message": "This operation conflicts with an existing record. Refresh and retry.",
                "fields": {},
            },
            status=409,
        )
        response["Cache-Control"] = "no-store, private"
        return response
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    message = (
        str(data.get("detail", "Correct the highlighted fields."))
        if isinstance(data, dict)
        else "Request could not be processed."
    )
    response.data = {
        "code": getattr(exc, "default_code", "request_error"),
        "message": message,
        "fields": data if isinstance(data, dict) and "detail" not in data else {},
    }
    response["Cache-Control"] = "no-store, private"
    return response
