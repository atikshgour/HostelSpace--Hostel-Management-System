# Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .fee_services import initiate, verify
from .models import FeeDue
from .payments import credentials
from .views import StudentAPIView


def attempt_data(attempt):
    return {'id': attempt.pk, 'status': attempt.status, 'created_at': attempt.created_at,
            'resolved_at': attempt.resolved_at}


def fee_data(fee):
    return {'id': fee.pk, 'description': fee.description, 'amount': str(fee.amount),
            'currency': fee.currency, 'status': fee.status, 'paid_at': fee.paid_at,
            'attempts': [attempt_data(item) for item in fee.attempts.all()]}


@method_decorator(never_cache, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FeeList(StudentAPIView):
    def get(self, request):
        fees = FeeDue.objects.filter(student=request.user).prefetch_related('attempts')
        return Response({'results': [fee_data(fee) for fee in fees]})


@method_decorator(never_cache, name='dispatch')
class FeeInitiate(StudentAPIView):
    def post(self, request, pk):
        attempt = initiate(request.user, pk)
        key, _ = credentials()
        return Response({'attempt_id': attempt.pk, 'order_id': attempt.provider_order_id,
                         'key_id': key, 'amount': int(attempt.amount * 100),
                         'currency': attempt.currency}, status=status.HTTP_201_CREATED)


@method_decorator(never_cache, name='dispatch')
class FeeVerify(StudentAPIView):
    def post(self, request, pk):
        allowed = {'payment_id', 'signature', 'cancelled'}
        if set(request.data) - allowed or type(request.data.get('cancelled', False)) is not bool:
            raise ValidationError({'payment': ['Invalid verification input.']})
        attempt = verify(request.user, pk, request.data.get('payment_id'),
                         request.data.get('signature'), request.data.get('cancelled', False))
        return Response(attempt_data(attempt))
