from django.db import transaction
from rest_framework.response import Response
from apps.accounts.serializers import ProtectedView
from apps.accounts.permissions import require
from apps.accounts.models import AuditEvent
from .models import *
from .serializers import *
from . import services
class Study(ProtectedView):
    def get(self,request):
        obj=StudyRoom.objects.first();return Response(StudySerializer(obj).data if obj else {'status':'Closed','timings':'','message':'No update published.'})
    @transaction.atomic
    def put(self,request):
        require(request.user,'DIRECTOR','CONTENT_STAFF','WARDEN');obj=StudyRoom.objects.select_for_update().first()
        s=self.validate(StudySerializer,request,instance=obj);s.save(id=1,updated_by=request.user)
        AuditEvent.objects.create(actor=request.user,action='study_room_updated',object_key='1',details=s.validated_data)
        return Response(s.data)
class Allocations(ProtectedView):
    def get(self,request):
        from apps.accounts.models import User
        require(request.user,'STUDENT','LAUNDRY_STAFF','WARDEN','DIRECTOR')
        q=User.objects.filter(role='STUDENT',is_active=True).select_related('student_profile').order_by('pk')
        if request.user.role=='STUDENT':q=q.filter(pk=request.user.pk)
        if request.user.role=='WARDEN':q=q.filter(student_profile__assigned_warden=request.user)
        days=services.default_days()
        return Response({'results':[services.schedule(u,days=days) for u in q]})
    def post(self,request):
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('Laundry groups are automatic; manual weekday assignment is disabled.')
class Records(ProtectedView):
    def get(self,request):
        require(request.user,'STUDENT','LAUNDRY_STAFF','WARDEN','DIRECTOR');q=LaundryRecord.objects.select_related('student').all()
        if request.user.role=='STUDENT':q=q.filter(student=request.user)
        if request.user.role=='WARDEN':q=q.filter(student__student_profile__assigned_warden=request.user)
        return self.rows(q,RecordSerializer,request)
    def post(self,request):
        require(request.user,'LAUNDRY_STAFF');s=self.validate(ReceiveInput,request);return Response(RecordSerializer(services.receive(request.user,s.validated_data)).data,status=201)
class Collect(ProtectedView):
    def post(self,request,pk):return Response(RecordSerializer(services.collect(request.user,pk)).data)

class Ready(ProtectedView):
    def post(self,request,pk):return Response(RecordSerializer(services.ready(request.user,pk)).data)

class Policy(ProtectedView):
    def get(self,request):
        from django.utils import timezone
        require(request.user,'STUDENT','LAUNDRY_STAFF','WARDEN','DIRECTOR')
        return Response({'turnaround_days':services.default_days(),'server_today':timezone.localdate()})
    @transaction.atomic
    def put(self,request):
        require(request.user,'LAUNDRY_STAFF');s=self.validate(PolicyInput,request)
        policy,_=LaundryPolicy.objects.update_or_create(pk=1,defaults={**s.validated_data,'updated_by':request.user})
        AuditEvent.objects.create(actor=request.user,action='laundry_policy_updated',object_key='1',details=s.validated_data)
        return Response({'turnaround_days':policy.turnaround_days})
