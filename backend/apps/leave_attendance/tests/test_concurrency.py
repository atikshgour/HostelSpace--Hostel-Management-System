"""PostgreSQL release gates. Skipped explicitly by the SQLite quick harness."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from django.db import connection, close_old_connections
from django.test import TransactionTestCase
from demo_accounts.models import User
from apps.leave_attendance import services
from apps.leave_attendance.models import Attendance, LeaveRequest
from .fixtures import fixtures

@skipUnless(connection.vendor=='postgresql','Requires real PostgreSQL row locks and uniqueness semantics.')
class ConcurrentTests(TransactionTestCase):
    def setUp(self): fixtures(self)
    def race(self, operation):
        barrier=Barrier(2)
        def worker():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try: operation();return 'ok'
                except services.Conflict: return 'conflict'
            finally: close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:worker(),range(2)))
        self.assertCountEqual(results,['ok','conflict'])
    def test_concurrent_attendance_accepts_once(self):
        self.race(lambda:services.submit_attendance(User.objects.get(pk=self.student.pk),self.session.pk,self.sample))
        self.assertEqual(Attendance.objects.filter(result='Accepted').count(),1)
    def test_concurrent_leave_finalizes_once(self):
        row=services.submit_leave(self.student,self.leave_data)
        self.race(lambda:services.decide_leave(User.objects.get(pk=self.warden.pk),row.pk,'Approved','Reviewed'))
        row.refresh_from_db();self.assertEqual(row.status,'Approved');self.assertEqual(row.transitions.count(),2)
