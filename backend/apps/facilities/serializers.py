from rest_framework import serializers
from apps.accounts.serializers import StrictModelSerializer,StrictSerializer
from apps.accounts.models import User
from .models import StudyRoom,LaundryAllocation,LaundryRecord
class StudySerializer(StrictModelSerializer):
    class Meta:
        model=StudyRoom;fields=['status','timings','message','updated_by','updated_at'];read_only_fields=['updated_by','updated_at']
class AllocationInput(StrictSerializer):
    student=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='STUDENT',is_active=True))
    weekday=serializers.ChoiceField(choices=[x[0] for x in LaundryAllocation._meta.get_field('weekday').choices])
class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=LaundryAllocation;fields=['id','student','weekday','assigned_by','updated_at']
class ReceiveInput(StrictSerializer):
    turnaround_days=serializers.IntegerField(min_value=1,max_value=14,required=False)
    student=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='STUDENT',is_active=True))
    item_details=serializers.CharField(max_length=1000)
    item_count=serializers.IntegerField(min_value=1,max_value=1000)
class RecordSerializer(serializers.ModelSerializer):
    student_name=serializers.SerializerMethodField()
    def get_student_name(self,obj):return obj.student.get_full_name() or obj.student.username
    class Meta:
        model=LaundryRecord;fields='__all__'

class PolicyInput(StrictSerializer):
    turnaround_days=serializers.IntegerField(min_value=1,max_value=14)
