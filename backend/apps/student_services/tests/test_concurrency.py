from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import TransactionTestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.student_services.models import MessAllocation, MessOption
from apps.student_services.services import select_mess


@skipUnless(connection.vendor == "postgresql", "Requires PostgreSQL row locking.")
class MessCapacityRace(TransactionTestCase):
    def test_last_place_cannot_be_double_booked(self):
        users = [
            User.objects.create_user(username="choice" + str(i), role="STUDENT")
            for i in range(2)
        ]
        staff = User.objects.create_user(username="allocation-staff", role="MESS_STAFF")
        option = MessOption.objects.create(name="One place", diet="Mixed", capacity=1)
        gate = Barrier(2)

        def choose(pk):
            close_old_connections()
            try:
                user = User.objects.get(pk=pk)
                o = MessOption.objects.get(pk=option.pk)
                gate.wait(timeout=10)
                try:
                    select_mess(staff, o, user)
                    return "selected"
                except ValidationError:
                    return "full"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            out = list(pool.map(choose, [u.pk for u in users]))
        self.assertEqual(sorted(out), ["full", "selected"])
        self.assertEqual(MessAllocation.objects.filter(option=option).count(), 1)
