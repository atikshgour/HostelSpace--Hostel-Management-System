# Shared error dependency for US-13 | Owner: Arin Singh | Independent review pending
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return Response(
            {'code': 'server_error', 'message': 'An unexpected error occurred.', 'fields': {}},
            status=500,
        )
    if isinstance(exc, ValidationError):
        fields = response.data if isinstance(response.data, dict) else {'non_field_errors': response.data}
        response.data = {
            'code': 'validation_error', 'message': 'Check the submitted fields.', 'fields': fields,
        }
    else:
        status_codes = {
            400: 'parse_error', 401: 'not_authenticated', 403: 'permission_denied',
            404: 'not_found', 405: 'method_not_allowed', 415: 'unsupported_media_type',
            429: 'throttled',
        }
        response.data = {
            'code': getattr(exc, 'default_code', status_codes.get(response.status_code, 'error')),
            'message': str(response.data.get('detail', 'Request failed.')),
            'fields': {},
        }
    return response
