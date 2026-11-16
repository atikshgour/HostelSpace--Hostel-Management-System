# Owner: Anvi Srinivas | Story: US-02 | Sprint: 1
import json
import re

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Role
from .views import error

PHONE_RE = re.compile(r"^\+?[0-9]{10,13}$")


def profile_payload(u):
    return {
        "name": u.get_full_name() or u.username,
        "username": u.username,
        "usn": u.usn,
        "room_number": u.room_number,
        "role": u.role,
        "phone": u.phone,
    }


@require_http_methods(["GET", "PATCH"])
def profile(request):
    u = request.user
    if not u.is_authenticated:
        return error("not_authenticated", "Please sign in.", 401)
    if u.role != Role.STUDENT:
        return error("forbidden", "Only students have a profile.", 403)

    if request.method == "PATCH":
        try:
            body = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return error("invalid_json", "Request body must be valid JSON.", 400)
        extra = [k for k in body if k != "phone"]
        if extra:
            return error("validation_error", "Only the phone number can be updated.", 400,
                         {k: "This field cannot be changed." for k in extra})
        phone = str(body.get("phone", "")).strip().replace(" ", "")
        if not PHONE_RE.match(phone):
            return error("validation_error", "Please fix the highlighted fields.", 400,
                         {"phone": "Enter 10 to 13 digits, optional leading +."})
        u.phone = phone
        u.save(update_fields=["phone"])

    response = JsonResponse(profile_payload(u))
    response["Cache-Control"] = "no-store"
    return response
