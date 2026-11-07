# Owner: Anvi Srinivas | Story: US-03 | Sprint: 2
import json
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from accounts.models import Role
from accounts.views import error

from .models import Contact, Notice, Rule

STAFF_ROLES = {Role.WARDEN, Role.CHIEF_WARDEN, Role.DIRECTOR}
PHONE_RE = re.compile(r"^\+?[0-9]{10,13}$")

# kind -> (model, ordering, [(field, type, max_len, required)])
KINDS = {
    "notices": (Notice, ("-created_at",), [("title", "str", 200, True), ("body", "str", 5000, True)]),
    "contacts": (Contact, ("name",), [("name", "str", 100, True), ("designation", "str", 100, True),
                                      ("phone", "phone", None, True), ("email", "email", None, False)]),
    "rules": (Rule, ("order", "id"), [("title", "str", 200, True), ("body", "str", 5000, True),
                                      ("order", "int", None, False)]),
}


def serialize(obj, spec):
    data = {"id": obj.id, "is_active": obj.is_active, "updated_at": obj.updated_at.isoformat()}
    for name, *_ in spec:
        data[name] = getattr(obj, name)
    return data


def clean(body, spec, partial):
    """Return (values, field_errors)."""
    values, errors = {}, {}
    allowed = {s[0] for s in spec} | {"is_active"}
    for k in body:
        if k not in allowed:
            errors[k] = "This field cannot be set."
    for name, typ, max_len, required in spec:
        if name not in body:
            if required and not partial:
                errors[name] = "This field is required."
            continue
        raw = body[name]
        if typ == "int":
            if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
                errors[name] = "Enter a whole number, 0 or more."
                continue
            values[name] = raw
            continue
        val = str(raw).strip()
        if typ == "phone":
            val = val.replace(" ", "")
        if not val and (required or typ == "phone"):
            errors[name] = "This field is required."
        elif typ == "phone" and not PHONE_RE.match(val):
            errors[name] = "Enter 10 to 13 digits, optional leading +."
        elif typ == "email" and val:
            try:
                validate_email(val)
            except ValidationError:
                errors[name] = "Enter a valid email address."
        elif max_len and len(val) > max_len:
            errors[name] = f"Keep this under {max_len} characters."
        if name not in errors:
            values[name] = val
    if "is_active" in body:
        if isinstance(body["is_active"], bool):
            values["is_active"] = body["is_active"]
        else:
            errors["is_active"] = "Must be true or false."
    return values, errors


def _prepare(request, kind):
    if not request.user.is_authenticated:
        return None, error("not_authenticated", "Please sign in.", 401)
    if kind not in KINDS:
        return None, error("not_found", "Unknown content type.", 404)
    return KINDS[kind], None


def _body(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, error("invalid_json", "Request body must be valid JSON.", 400)


def _is_staff(user):
    return user.role in STAFF_ROLES


@require_http_methods(["GET", "POST"])
def collection(request, kind):
    cfg, err = _prepare(request, kind)
    if err:
        return err
    model, ordering, spec = cfg

    if request.method == "GET":
        qs = model.objects.all()
        if not _is_staff(request.user):
            qs = qs.filter(is_active=True)
        response = JsonResponse({"items": [serialize(o, spec) for o in qs.order_by(*ordering)]})
        response["Cache-Control"] = "no-store"
        return response

    if not _is_staff(request.user):
        return error("forbidden", "Only hostel staff can manage this content.", 403)
    body, bad = _body(request)
    if bad:
        return bad
    values, errors = clean(body, spec, partial=False)
    if errors:
        return error("validation_error", "Please fix the highlighted fields.", 400, errors)
    obj = model.objects.create(created_by=request.user, **values)
    return JsonResponse(serialize(obj, spec), status=201)


@require_http_methods(["PATCH"])
def detail(request, kind, item_id):
    cfg, err = _prepare(request, kind)
    if err:
        return err
    model, _, spec = cfg
    if not _is_staff(request.user):
        return error("forbidden", "Only hostel staff can manage this content.", 403)
    try:
        obj = model.objects.get(pk=item_id)
    except model.DoesNotExist:
        return error("not_found", "Item not found.", 404)
    body, bad = _body(request)
    if bad:
        return bad
    values, errors = clean(body, spec, partial=True)
    if errors:
        return error("validation_error", "Please fix the highlighted fields.", 400, errors)
    for k, v in values.items():
        setattr(obj, k, v)
    obj.save()
    return JsonResponse(serialize(obj, spec))
