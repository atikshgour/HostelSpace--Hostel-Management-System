import re
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from apps.accounts.permissions import require
from apps.accounts.models import AuditEvent
from .models import LaundryRecord,LaundryPolicy
DAYS=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
def default_days():
    return LaundryPolicy.objects.values_list("turnaround_days",flat=True).first() or 3
def schedule(student,today=None,days=None):
    today=today or timezone.localdate()
    days=default_days() if days is None else days
    profile=getattr(student,'student_profile',None)
    numbers=re.findall(r'\d+',profile.srn if profile else '')
    number=int(numbers[-1]) if numbers else student.pk
    day=(max(1,number)-1)%7
    drop=today+timedelta(days=(day-today.weekday())%7)
    return {'id':student.pk,'student':student.pk,'student_name':student.get_full_name() or student.username,'srn':profile.srn if profile else '', 'room':profile.room if profile else '', 'group_number':day+1,'weekday':DAYS[day],'next_dropoff_date':drop,'next_return_date':drop+timedelta(days=days),'turnaround_days':days}
@transaction.atomic
def receive(user,data):
    require(user,'LAUNDRY_STAFF')
    data=dict(data)
    days=data.pop('turnaround_days',None) or default_days()
    plan=schedule(data['student'],days=days)
    record=LaundryRecord.objects.create(**data,allocation_snapshot=plan['weekday'],group_number=plan['group_number'],expected_return_date=timezone.localdate()+timedelta(days=days),received_by=user)
    AuditEvent.objects.create(actor=user,action='laundry_received',object_key=str(record.pk),details={'group':record.group_number,'expected_return':str(record.expected_return_date)})
    return record
@transaction.atomic
def ready(user,pk):
    require(user,'LAUNDRY_STAFF')
    r=get_object_or_404(LaundryRecord.objects.select_for_update(),pk=pk)
    if r.status in ('Ready','Collected'):return r
    r.status='Ready';r.ready_at=timezone.now();r.save(update_fields=['status','ready_at'])
    AuditEvent.objects.create(actor=user,action='laundry_ready',object_key=str(pk))
    return r
@transaction.atomic
def collect(user,pk):
    require(user,'LAUNDRY_STAFF')
    r=get_object_or_404(LaundryRecord.objects.select_for_update(),pk=pk)
    if r.status=='Collected':return r
    if r.status!='Ready':raise ValidationError({'status':'Mark this batch ready before confirming collection.'})
    r.status='Collected';r.collected_by=user;r.collected_at=timezone.now();r.save(update_fields=['status','collected_by','collected_at'])
    AuditEvent.objects.create(actor=user,action='laundry_collected',object_key=str(pk))
    return r
