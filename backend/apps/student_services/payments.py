# Owner: Atiksh Gour | US-16 | Sprint 5 | Reviewer: Anvi Srinivas
"""Razorpay test-mode boundary. Provider data is always checked on the server."""
import base64
import hashlib
import hmac
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from django.core.exceptions import ImproperlyConfigured


class ProviderError(Exception):
    pass


def credentials():
    key = os.environ.get('RAZORPAY_TEST_KEY_ID', '')
    secret = os.environ.get('RAZORPAY_TEST_KEY_SECRET', '')
    if not key.startswith('rzp_test_') or not secret:
        raise ImproperlyConfigured('Razorpay test credentials are not configured.')
    return key, secret


def _request(path, method='GET', payload=None):
    key, secret = credentials()
    encoded = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    request = urllib.request.Request(
        f'https://api.razorpay.com/v1/{path}',
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={'Authorization': f'Basic {encoded}', 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise ProviderError('Test payment provider is temporarily unavailable.') from exc


def create_order(fee):
    amount_paise = int(fee.amount * 100)
    order = _request('orders', 'POST', {
        'amount': amount_paise, 'currency': fee.currency,
        'receipt': f'fee-{fee.pk}', 'payment_capture': 1,
    })
    if (not str(order.get('id', '')).startswith('order_') or
            order.get('amount') != amount_paise or order.get('currency') != fee.currency):
        raise ProviderError('Test provider returned an invalid order.')
    return order['id']


def fetch_payment(payment_id):
    if not isinstance(payment_id, str) or not payment_id.startswith('pay_') or len(payment_id) > 100:
        raise ProviderError('Invalid payment reference.')
    return _request(f'payments/{urllib.parse.quote(payment_id, safe="")}')


def fetch_order_payments(order_id):
    if not isinstance(order_id, str) or not order_id.startswith('order_') or len(order_id) > 100:
        raise ProviderError('Invalid order reference.')
    return _request(f'orders/{urllib.parse.quote(order_id, safe="")}/payments').get('items', [])


def valid_checkout_signature(order_id, payment_id, signature):
    _, secret = credentials()
    expected = hmac.new(secret.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()
    return isinstance(signature, str) and hmac.compare_digest(expected, signature)
