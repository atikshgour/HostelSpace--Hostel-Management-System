"""Idempotent synthetic records. Password is supplied privately; no reset of existing passwords."""
import os,getpass
from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand,CommandError
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import User,StudentProfile
from apps.information.models import Content,Rule
from apps.facilities.models import StudyRoom,LaundryAllocation
from apps.student_services.models import MessAllocation,Coupon,FeeDue,MessOption
class Command(BaseCommand):
    help='Create synthetic local demo records. Requires DEBUG=True; never resets existing accounts.'
    @transaction.atomic
    def handle(self,*args,**options):
        if not settings.DEBUG:raise CommandError('Demo seeding is local-only.')
        password=os.environ.get('HOSTELSPACE_DEMO_PASSWORD') or getpass.getpass('Password for new demo users (12+ characters): ')
        if len(password)<12:raise CommandError('Use at least 12 characters.')
        def user(name,role,**extra):
            u,created=User.objects.get_or_create(username=name,defaults={'role':role,**extra})
            if created:u.set_password(password);u.save()
            return u
        director=user('director','DIRECTOR',first_name='Director')
        chief=user('chief','CHIEF_WARDEN',first_name='Anil',last_name='Kumar')
        warden=user('warden','WARDEN',chief_warden=chief,first_name='Meera',last_name='Rao')
        student=user('student','STUDENT',first_name='Arin',last_name='V.')
        second=user('student2','STUDENT',first_name='Rohan',last_name='S.')
        laundry=user('laundry','LAUNDRY_STAFF');maintenance=user('maintenance','MAINTENANCE_STAFF');mess=user('mess','MESS_STAFF');user('content','CONTENT_STAFF')
        for i,u in enumerate([student,second]):StudentProfile.objects.get_or_create(user=u,defaults={'srn':f'DEMO-{i+1:03}','room':str(204+i),'assigned_warden':warden,'phone':'+919000000001'})
        Content.objects.get_or_create(kind='notice',title='Welcome to HostelSpace',defaults={'body':'Your hostel notices, services and requests are now available in one portal.','updated_by':director})
        Content.objects.get_or_create(kind='contact',title='Hostel office',defaults={'body':'Ground floor, Block A. Office hours: 9 AM – 5 PM.','updated_by':director})
        Content.objects.get_or_create(kind='information',title='Quiet hours',defaults={'body':'Please maintain quiet in shared areas between 10 PM and 6 AM.','updated_by':director})
        Rule.objects.get_or_create(title='Return before 8 PM',defaults={'body':'Obtain approved leave for overnight absence.','weightage':Decimal('2.50')})
        StudyRoom.objects.get_or_create(pk=1,defaults={'status':'Open','timings':'6 AM – 10 PM','message':'Please keep the room quiet.','updated_by':director})
        LaundryAllocation.objects.get_or_create(student=student,defaults={'weekday':'Saturday','assigned_by':laundry})
        MessAllocation.objects.get_or_create(student=student,defaults={'mess_name':'Main vegetarian mess','assigned_by':mess})
        for name,diet,description in [('Main vegetarian mess','Vegetarian','Vegetarian meals with seasonal vegetables and dal.'),('Central mixed mess','Mixed','Vegetarian choices with non-vegetarian options on selected days.')]:
            MessOption.objects.get_or_create(name=name,defaults={'diet':diet,'description':description,'capacity':100,'breakfast':'Idli / dosa, fruit and tea','lunch':'Rice, roti, dal and vegetables','dinner':'Roti, rice and rotating curry'})
        today=timezone.localdate()
        Coupon.objects.get_or_create(code='DEMO-MEAL-001',defaults={'student':student,'valid_from':today,'valid_to':today+timedelta(days=30),'created_by':mess})
        FeeDue.objects.get_or_create(student=student,title='Hostel term fee — synthetic',defaults={'amount':Decimal('1500.00'),'due_date':today+timedelta(days=15)})
        self.stdout.write(self.style.SUCCESS('Demo users: director, chief, warden, student, student2, laundry, maintenance, mess, content. Existing passwords were not changed.'))
