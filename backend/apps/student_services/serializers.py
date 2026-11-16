# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
from decimal import Decimal

from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.serializers import StrictModelSerializer, StrictSerializer

from .models import (
    Complaint,
    ComplaintTransition,
    Coupon,
    FeeDue,
    MessAllocation,
    MessChoiceEvent,
    MessOption,
    PaymentAttempt,
)


class ComplaintInput(StrictSerializer):
    category = serializers.ChoiceField(
        choices=[x[0] for x in Complaint._meta.get_field("category").choices]
    )
    description = serializers.CharField(max_length=3000)


class TransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintTransition
        fields = ["id", "actor", "from_status", "to_status", "remarks", "occurred_at"]


class ComplaintSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assigned_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    def get_assigned_name(self, obj):
        return (
            (obj.assigned_to.get_full_name() or obj.assigned_to.username)
            if obj.assigned_to
            else None
        )

    transitions = TransitionSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = "__all__"


class AssignInput(StrictSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="MAINTENANCE_STAFF", is_active=True)
    )


class ProgressInput(StrictSerializer):
    status = serializers.ChoiceField(choices=["In Progress", "Resolved"])
    remarks = serializers.CharField(max_length=2000)


class MessInput(StrictSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="STUDENT", is_active=True)
    )
    mess_name = serializers.CharField(max_length=100)


class MessSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    class Meta:
        model = MessAllocation
        fields = "__all__"


class CouponSerializer(StrictModelSerializer):
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="STUDENT", is_active=True)
    )

    class Meta:
        model = Coupon
        fields = [
            "id",
            "student",
            "student_name",
            "code",
            "valid_from",
            "valid_to",
            "active",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        a = data.get("valid_from", getattr(self.instance, "valid_from", None))
        b = data.get("valid_to", getattr(self.instance, "valid_to", None))
        if a and b and b < a:
            raise serializers.ValidationError({"valid_to": "End must follow start."})
        return data


class FeeSerializer(StrictModelSerializer):
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="STUDENT", is_active=True)
    )
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.01")
    )
    currency = serializers.ChoiceField(choices=["INR"])

    class Meta:
        model = FeeDue
        fields = [
            "id",
            "student",
            "student_name",
            "title",
            "amount",
            "currency",
            "due_date",
            "status",
        ]
        read_only_fields = ["id", "status"]


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAttempt
        fields = "__all__"


class InitiateInput(StrictSerializer):
    fee = serializers.IntegerField(min_value=1)


class VerifyInput(StrictSerializer):
    attempt = serializers.UUIDField()
    payment_id = serializers.CharField(max_length=100)
    signature = serializers.CharField(max_length=128)


class SimulateInput(StrictSerializer):
    attempt = serializers.UUIDField()
    outcome = serializers.ChoiceField(choices=["Success", "Failed", "Cancelled"])


class MessOptionSerializer(StrictModelSerializer):
    enrolled = serializers.IntegerField(read_only=True)
    available = serializers.SerializerMethodField()

    def get_available(self, obj):
        return max(
            0,
            obj.capacity
            - getattr(
                obj, "enrolled", obj.allocations.filter(student__is_active=True).count()
            ),
        )

    capacity = serializers.IntegerField(min_value=1, max_value=100000)

    class Meta:
        model = MessOption
        fields = [
            "id",
            "name",
            "diet",
            "description",
            "capacity",
            "breakfast",
            "lunch",
            "dinner",
            "timings",
            "active",
            "enrolled",
            "available",
        ]
        read_only_fields = ["id"]


class MessSelectInput(StrictSerializer):
    option = serializers.PrimaryKeyRelatedField(queryset=MessOption.objects.all())
    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="STUDENT", is_active=True), required=False
    )


class MessChoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    class Meta:
        model = MessChoiceEvent
        fields = [
            "id",
            "student",
            "student_name",
            "old_mess",
            "new_mess",
            "occurred_at",
        ]
