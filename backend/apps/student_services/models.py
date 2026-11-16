# Owner: Atiksh Gour | US-13,US-14,US-15,US-16 | Dev sprint 2; 3 | SRS sprint 4; 5 | Reviewer: Anvi Srinivas (pending)
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

U = settings.AUTH_USER_MODEL


class AppendOnlyEvents(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError("Operational history is append-only.")

    def delete(self):
        raise ValidationError("Operational history is append-only.")

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError("Operational history is append-only.")


class ImmutableEvent(models.Model):
    objects = AppendOnlyEvents.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError("Operational history is append-only.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Operational history is append-only.")


class Complaint(models.Model):
    student = models.ForeignKey(U, on_delete=models.PROTECT, related_name="complaints")
    room_snapshot = models.CharField(max_length=120)
    category = models.CharField(
        max_length=20,
        choices=[
            (x, x) for x in ["Electrical", "Plumbing", "Furniture", "Cleaning", "Other"]
        ],
    )
    description = models.TextField(max_length=3000)
    status = models.CharField(
        max_length=12,
        default="Open",
        choices=[(x, x) for x in ["Open", "In Progress", "Resolved"]],
    )
    assigned_to = models.ForeignKey(
        U,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="assigned_complaints",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]


class ComplaintTransition(ImmutableEvent):
    complaint = models.ForeignKey(
        Complaint, on_delete=models.PROTECT, related_name="transitions"
    )
    actor = models.ForeignKey(U, on_delete=models.PROTECT)
    from_status = models.CharField(max_length=12, blank=True)
    to_status = models.CharField(max_length=12)
    remarks = models.CharField(max_length=2000)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["occurred_at", "pk"]


class MessAllocation(models.Model):
    option = models.ForeignKey(
        "MessOption",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="allocations",
    )
    student = models.OneToOneField(U, on_delete=models.PROTECT)
    mess_name = models.CharField(max_length=100)
    assigned_by = models.ForeignKey(U, on_delete=models.PROTECT, related_name="+")
    updated_at = models.DateTimeField(auto_now=True)


class Coupon(models.Model):
    student = models.ForeignKey(U, on_delete=models.PROTECT)
    code = models.CharField(max_length=80, unique=True)
    valid_from = models.DateField()
    valid_to = models.DateField()
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(U, on_delete=models.PROTECT, related_name="+")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(valid_to__gte=F("valid_from")), name="coupon_valid_dates"
            )
        ]


class FeeDue(models.Model):
    student = models.ForeignKey(U, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    due_date = models.DateField()
    status = models.CharField(
        max_length=6, default="Unpaid", choices=[("Unpaid", "Unpaid"), ("Paid", "Paid")]
    )

    class Meta:
        ordering = ["due_date", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0), name="positive_fee_amount"
            )
        ]


class PaymentAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fee = models.ForeignKey(FeeDue, on_delete=models.PROTECT, related_name="attempts")
    order_id = models.CharField(max_length=100, unique=True)
    provider_reference = models.CharField(max_length=100, unique=True, null=True)
    provider = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=10,
        default="Pending",
        choices=[(x, x) for x in ["Pending", "Success", "Failed", "Cancelled"]],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["fee"],
                condition=Q(status="Success"),
                name="one_successful_attempt_per_fee",
            )
        ]


class MessOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    diet = models.CharField(
        max_length=20, choices=[("Vegetarian", "Vegetarian"), ("Mixed", "Mixed")]
    )
    description = models.CharField(max_length=500, blank=True)
    capacity = models.PositiveIntegerField(default=100)
    breakfast = models.CharField(max_length=300, blank=True)
    lunch = models.CharField(max_length=300, blank=True)
    dinner = models.CharField(max_length=300, blank=True)
    timings = models.CharField(
        max_length=200, default="Breakfast 7–9 AM · Lunch 12–2 PM · Dinner 7–9 PM"
    )
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=Q(capacity__gt=0), name="mess_positive_capacity"
            )
        ]


class MessChoiceEvent(ImmutableEvent):
    student = models.ForeignKey(U, on_delete=models.PROTECT)
    actor = models.ForeignKey(U, on_delete=models.PROTECT, related_name="+")
    old_mess = models.CharField(max_length=100, blank=True)
    new_mess = models.CharField(max_length=100)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_at", "-pk"]
