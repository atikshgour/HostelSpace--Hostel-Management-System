from rest_framework.views import exception_handler

def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    data = response.data
    message = str(data.get('detail', 'Correct the highlighted fields.')) if isinstance(data, dict) else 'Request could not be processed.'
    response.data = {'code': getattr(exc, 'default_code', 'request_error'), 'message': message,
                     'fields': data if isinstance(data, dict) and 'detail' not in data else {}}
    response['Cache-Control'] = 'no-store, private'
    return response
