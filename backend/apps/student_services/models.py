# Owner: Atiksh Gour | US-13/14 | Sprint 4 (development plan: 2) | Reviewer: Anvi Srinivas
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ComplaintCategory(models.Model):
    code = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = 'Open', 'Open'
        IN_PROGRESS = 'In Progress', 'In Progress'
        RESOLVED = 'Resolved', 'Resolved'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='complaints',
    )
    room = models.CharField(max_length=32)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.PROTECT)
    description = models.CharField(max_length=2000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name='assigned_complaints',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [models.Index(fields=['student', '-created_at', '-id'], name='complaint_student_created')]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(description__regex=r'^\s*$'),
                name='complaint_description_not_blank',
            ),
            models.CheckConstraint(
                condition=~models.Q(room__regex=r'^\s*$'),
                name='complaint_room_not_blank',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['Open', 'In Progress', 'Resolved']),
                name='complaint_valid_status',
            ),
        ]


class AppendOnlyTransitions(models.QuerySet):
    def update(self, **kwargs):
        raise ValidationError('Complaint history is append-only.')

    def delete(self):
        raise ValidationError('Complaint history is append-only.')

    def bulk_update(self, objs, fields, batch_size=None):
        raise ValidationError('Complaint history is append-only.')


class ComplaintTransition(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.PROTECT, related_name='history')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    old_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16, choices=Complaint.Status.choices)
    remarks = models.CharField(max_length=500)
    old_assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name='+',
    )
    new_assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT,
        related_name='+',
    )

    objects = AppendOnlyTransitions.as_manager()

    class Meta:
        ordering = ['created_at', 'id']

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise ValidationError('Complaint history is append-only.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Complaint history is append-only.')
