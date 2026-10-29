# Owner: Atiksh Gour | US-15 | Sprint 5 | Reviewer: Anvi Srinivas
from collections.abc import Mapping

from rest_framework import serializers

from apps.accounts.models import User

from .models import Coupon, MessAllocation


class StrictMessSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError({key: ['This field is not accepted.'] for key in sorted(unknown)})
            for name in ('code', 'mess_name'):
                if name in data and not isinstance(data[name], str):
                    raise serializers.ValidationError({name: ['Expected a string.']})
            if 'is_active' in data and not isinstance(data['is_active'], bool):
                raise serializers.ValidationError({'is_active': ['Expected a boolean.']})
        return super().to_internal_value(data)


class MessDatesInput(StrictMessSerializer):
    valid_from = serializers.DateField()
    valid_until = serializers.DateField()
    is_active = serializers.BooleanField(default=True)

    def validate(self, attrs):
        start = attrs.get('valid_from', getattr(self.instance, 'valid_from', None))
        end = attrs.get('valid_until', getattr(self.instance, 'valid_until', None))
        if start is not None and end is not None and end < start:
            raise serializers.ValidationError({'valid_until': ['Must be on or after valid_from.']})
        return attrs


class AllocationInput(MessDatesInput):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, role=User.Role.STUDENT),
        pk_field=serializers.IntegerField(min_value=1),
    )
    mess_name = serializers.CharField(max_length=100, allow_blank=False)


class AllocationUpdateInput(MessDatesInput):
    mess_name = serializers.CharField(max_length=100, allow_blank=False)
    expected_version = serializers.IntegerField(min_value=1)


class CouponInput(MessDatesInput):
    allocation = serializers.PrimaryKeyRelatedField(
        queryset=MessAllocation.objects.all(), pk_field=serializers.IntegerField(min_value=1),
    )
    code = serializers.CharField(max_length=80, allow_blank=False)


class CouponUpdateInput(MessDatesInput):
    code = serializers.CharField(max_length=80, allow_blank=False)
    expected_version = serializers.IntegerField(min_value=1)


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessAllocation
        fields = ['id', 'student', 'mess_name', 'valid_from', 'valid_until', 'is_active',
                  'version', 'updated_by', 'updated_at']
        read_only_fields = fields


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'allocation', 'code', 'valid_from', 'valid_until', 'is_active',
                  'version', 'updated_by', 'updated_at']
        read_only_fields = fields


class MessStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = fields
