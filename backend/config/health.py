# Owner: Atiksh | US-20 foundation | Sprint 1
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


@never_cache
@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except DatabaseError:
        return JsonResponse(
            {'code': 'unavailable', 'message': 'Database unavailable', 'fields': {}},
            status=503,
        )
    return JsonResponse({'status': 'ok'})
