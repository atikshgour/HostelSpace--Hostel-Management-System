from django.conf import settings
from django.db import models
from django.db.models import Q
U=settings.AUTH_USER_MODEL
class StudyRoom(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1,editable=False)
    status=models.CharField(max_length=6,choices=[('Open','Open'),('Closed','Closed')],default='Closed')
    timings=models.CharField(max_length=200,blank=True)
    message=models.CharField(max_length=500,blank=True)
    updated_by=models.ForeignKey(U,on_delete=models.PROTECT)
    updated_at=models.DateTimeField(auto_now=True)
class LaundryAllocation(models.Model):
    student=models.OneToOneField(U,on_delete=models.PROTECT,related_name='laundry_allocation')
    weekday=models.CharField(max_length=9,choices=[(x,x) for x in ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']])
    assigned_by=models.ForeignKey(U,on_delete=models.PROTECT,related_name='+')
    updated_at=models.DateTimeField(auto_now=True)
class LaundryRecord(models.Model):
    student=models.ForeignKey(U,on_delete=models.PROTECT)
    item_details=models.CharField(max_length=1000)
    item_count=models.PositiveIntegerField()
    allocation_snapshot=models.CharField(max_length=9)
    group_number=models.PositiveSmallIntegerField(null=True)
    expected_return_date=models.DateField(null=True)
    ready_at=models.DateTimeField(null=True)
    status=models.CharField(max_length=10,default='Received',choices=[('Received','Received'),('Ready','Ready'),('Collected','Collected')])
    received_by=models.ForeignKey(U,on_delete=models.PROTECT,related_name='+')
    received_at=models.DateTimeField(auto_now_add=True)
    collected_by=models.ForeignKey(U,null=True,on_delete=models.PROTECT,related_name='+')
    collected_at=models.DateTimeField(null=True)
    class Meta:
        ordering=['-received_at','-pk']
        constraints=[models.CheckConstraint(condition=Q(item_count__gt=0),name='laundry_positive_items')]

class LaundryPolicy(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1,editable=False)
    turnaround_days=models.PositiveSmallIntegerField(default=3)
    updated_by=models.ForeignKey(U,on_delete=models.PROTECT,null=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints=[models.CheckConstraint(condition=Q(turnaround_days__gte=1,turnaround_days__lte=14),name='laundry_turnaround_range')]
