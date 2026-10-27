# Owner: Atiksh Gour | US-13 | Sprint 4 | Reviewer: Anvi Srinivas
from .models import Complaint, ComplaintCategory


def active_categories():
    return ComplaintCategory.objects.filter(is_active=True)


def own_complaints(student):
    return (
        Complaint.objects.filter(student_id=student.pk)
        .select_related('category')
        .prefetch_related('history')
    )
