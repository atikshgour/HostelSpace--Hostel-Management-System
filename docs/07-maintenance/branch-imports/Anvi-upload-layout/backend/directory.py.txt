# Owner: Anvi Srinivas | Story: US-04 (Sprint 1) | Director user lifecycle and role assignment
import json

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Role, User
from .views import error

VALID_ROLES = {r.value for r in Role}


def row(u):
    return {
        "id": u.id,
        "username": u.username,
        "name": u.get_full_name() or u.username,
        "role": u.role,
        "is_active": u.is_active,
    }


def director_only(request):
    if not request.user.is_authenticated:
        return error("not_authenticated", "Please sign in.", 401)
    if request.user.role != Role.DIRECTOR:
        return error("forbidden", "Only the Hostel Director can manage users.", 403)
    return None


def read_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, error("invalid_json", "Request body must be valid JSON.", 400)


@require_http_methods(["GET", "POST"])
def users(request):
    denied = director_only(request)
    if denied:
        return denied

    if request.method == "GET":
        data = [row(u) for u in User.objects.order_by("username")]
        response = JsonResponse({"users": data})
        response["Cache-Control"] = "no-store"
        return response

    body, bad = read_json(request)
    if bad:
        return bad
    username = (body.get("username") or "").strip()
    name = (body.get("name") or "").strip()
    role = body.get("role") or ""
    password = body.get("password") or ""
    fields = {}
    if not username:
        fields["username"] = "Username is required."
    if not name:
        fields["name"] = "Name is required."
    if role not in VALID_ROLES:
        fields["role"] = "Choose a valid role."
    if len(password) < 8:
        fields["password"] = "Password must be at least 8 characters."
    if fields:
        return error("validation_error", "Please fix the highlighted fields.", 400, fields)

    try:
        u = User.objects.create_user(username=username, password=password, first_name=name, role=role)
    except IntegrityError:
        return error("validation_error", "Please fix the highlighted fields.", 400,
                     {"username": "This username is already taken."})
    return JsonResponse(row(u), status=201)


@require_http_methods(["PATCH"])
def user_detail(request, user_id):
    denied = director_only(request)
    if denied:
        return denied
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return error("not_found", "User not found.", 404)

    body, bad = read_json(request)
    if bad:
        return bad
    extra = [k for k in body if k not in ("role", "is_active")]
    if extra:
        return error("validation_error", "Only role and active status can be changed.", 400,
                     {k: "This field cannot be changed." for k in extra})

    if target.pk == request.user.pk:
        return error("forbidden", "You cannot change your own role or status.", 403)

    if "role" in body:
        if body["role"] not in VALID_ROLES:
            return error("validation_error", "Choose a valid role.", 400, {"role": "Choose a valid role."})
        target.role = body["role"]
    if "is_active" in body:
        if not isinstance(body["is_active"], bool):
            return error("validation_error", "is_active must be true or false.", 400,
                         {"is_active": "Must be true or false."})
        target.is_active = body["is_active"]
    target.save(update_fields=["role", "is_active"])
    return JsonResponse(row(target))
