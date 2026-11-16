"""Atiksh Gour | US-20: synthetic local/CI fixtures; never resets existing users."""
import os
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import StudentProfile, User
from apps.student_services.models import FeeDue


class Command(BaseCommand):
    help = 'Seed service tests in a disposable local database only.'
    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Synthetic seeding requires local DEBUG mode.')
        password = os.environ.get('HOSTELSPACE_DEMO_PASSWORD', '')
        if len(password) < 12:
            raise CommandError('Supply a private HOSTELSPACE_DEMO_PASSWORD (12+ characters).')
        users = {}
        for name, role in [('director','DIRECTOR'),('warden','WARDEN'),('student','STUDENT'),('student2','STUDENT'),('maintenance','MAINTENANCE_STAFF'),('mess','MESS_STAFF')]:
            u, created = User.objects.get_or_create(username=name, defaults={'role':role})
            if created:
                u.set_password(password)
                u.save()
            users[name] = u
        for n, name in enumerate(['student','student2']):
            StudentProfile.objects.get_or_create(user=users[name], defaults={'srn':f'DEMO-{n}', 'room':f'20{n}', 'assigned_warden':users['warden']})
        FeeDue.objects.get_or_create(student=users['student'],title='Synthetic term fee',defaults={'amount':Decimal('100.00'),'due_date':timezone.localdate()})
        self.stdout.write('Synthetic service fixtures ready; existing passwords unchanged.')
