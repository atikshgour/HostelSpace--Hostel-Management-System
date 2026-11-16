# Owner: Anvi Srinivas | Story: US-01 | Sprint: 1
import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST


def error(code, message, status, fields=None):
    return JsonResponse({"code": code, "message": message, "fields": fields or {}}, status=status)


def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "name": user.get_full_name() or user.username,
        "role": user.role,
    }


@require_GET
@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
def login_view(request):
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return error("invalid_json", "Request body must be valid JSON.", 400)

    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    fields = {}
    if not username:
        fields["username"] = "Username is required."
    if not password:
        fields["password"] = "Password is required."
    if fields:
        return error("validation_error", "Please fix the highlighted fields.", 400, fields)

    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        return error("invalid_credentials", "Incorrect username or password.", 401)

    login(request, user)
    return JsonResponse(user_payload(user))


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "signed_out"})


@require_GET
def me(request):
    if not request.user.is_authenticated:
        return error("not_authenticated", "Please sign in.", 401)
    response = JsonResponse(user_payload(request.user))
    response["Cache-Control"] = "no-store"
    return response
