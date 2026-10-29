# Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from apps.accounts.models import User

from .mess_serializers import (
    AllocationInput,
    AllocationUpdateInput,
    CouponInput,
    CouponUpdateInput,
)
from .models import Coupon, MessAllocation


def _actor(actor):
    current = User.objects.select_for_update(no_key=True).filter(pk=actor.pk).first()
    if current is None or not current.is_active or current.role != User.Role.MESS:
        raise PermissionDenied('An active Mess Staff account is required.')
    return current


def _validate(serializer):
    serializer.is_valid(raise_exception=True)
    return dict(serializer.validated_data)


def _update(record, values, actor):
    expected = values.pop('expected_version', None)
    if expected != record.version:
        raise ValidationError({'expected_version': ['Record changed; reload before retrying.']})
    if not values:
        raise ValidationError({'non_field_errors': ['Provide a field to update.']})
    for key, value in values.items():
        setattr(record, key, value)
    record.version += 1
    record.updated_by = actor
    record.save()
    return record


@transaction.atomic
def create_allocation(*, actor, data):
    actor = _actor(actor)
    values = _validate(AllocationInput(data=data))
    student = User.objects.select_for_update(no_key=True).filter(
        pk=values['student'].pk, is_active=True, role=User.Role.STUDENT,
    ).first()
    if student is None:
        raise ValidationError({'student': ['Select an active student.']})
    if MessAllocation.objects.filter(student=student).exists():
        raise ValidationError({'student': ['This student already has an allocation; update it instead.']})
    return MessAllocation.objects.create(**values, updated_by=actor)


@transaction.atomic
def update_allocation(*, actor, pk, data):
    actor = _actor(actor)
    record = MessAllocation.objects.select_for_update().filter(pk=pk).first()
    if record is None:
        raise NotFound('Allocation not found.')
    values = _validate(AllocationUpdateInput(instance=record, data=data, partial=True))
    return _update(record, values, actor)


@transaction.atomic
def create_coupon(*, actor, data):
    actor = _actor(actor)
    values = _validate(CouponInput(data=data))
    allocation = MessAllocation.objects.select_for_update().get(pk=values['allocation'].pk)
    if Coupon.objects.filter(allocation=allocation, code=values['code']).exists():
        raise ValidationError({'code': ['This allocation already has this coupon code.']})
    return Coupon.objects.create(**values, updated_by=actor)


@transaction.atomic
def update_coupon(*, actor, pk, data):
    actor = _actor(actor)
    allocation_id = Coupon.objects.filter(pk=pk).values_list('allocation_id', flat=True).first()
    if allocation_id is None:
        raise NotFound('Coupon not found.')
    # Parent-before-child order matches coupon creation and allocation changes.
    MessAllocation.objects.select_for_update().get(pk=allocation_id)
    record = Coupon.objects.select_for_update().get(pk=pk)
    values = _validate(CouponUpdateInput(instance=record, data=data, partial=True))
    if 'code' in values and Coupon.objects.filter(
        allocation_id=allocation_id, code=values['code'],
    ).exclude(pk=pk).exists():
        raise ValidationError({'code': ['This allocation already has this coupon code.']})
    return _update(record, values, actor)
