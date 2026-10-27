from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from demo_accounts.models import User, StudentProfile, Rule
from apps.leave_attendance.models import AttendanceSession

def fixtures(case):
    case.chief=User.objects.create_user(username='chief',role='CHIEF_WARDEN')
    case.warden=User.objects.create_user(username='warden',role='WARDEN',chief_warden=case.chief)
    case.other=User.objects.create_user(username='other',role='WARDEN',chief_warden=case.chief)
    case.student=User.objects.create_user(username='student',role='STUDENT')
    case.stranger=User.objects.create_user(username='stranger',role='STUDENT')
    for i,(u,w) in enumerate([(case.student,case.warden),(case.stranger,case.other)]):
        StudentProfile.objects.create(user=u,srn=f'LOCAL-{i}',room=f'DEMO-{i}',assigned_warden=w)
    case.rule=Rule.objects.create(title='Demo rule',weightage=Decimal('2.50'))
    now=timezone.now()
    case.session=AttendanceSession.objects.create(title='Demo session',warden=case.warden,opens_at=now-timedelta(minutes=5),closes_at=now+timedelta(minutes=5),centre_latitude=12.0,centre_longitude=77.0,radius_m=100,max_accuracy_m=50,max_sample_age_seconds=60)
    case.sample=dict(latitude=12.0,longitude=77.0,accuracy_m=5,sampled_at=now)
    case.leave_data=dict(start_date=now.date(),end_date=now.date()+timedelta(days=1),reason='Family visit')
