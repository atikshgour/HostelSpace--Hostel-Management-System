# Synthetic DEMO accounts for development only. Change/delete before any real use.
import os

from django.contrib.auth.hashers import make_password
from django.db import migrations

DEMO = [
    ("student1", "student", "Demo Student"),
    ("warden1", "warden", "Demo Warden"),
    ("chief1", "chief_warden", "Demo Chief Warden"),
    ("director1", "director", "Demo Director"),
    ("maint1", "maintenance", "Demo Maintenance"),
    ("mess1", "mess", "Demo Mess"),
    ("laundry1", "laundry", "Demo Laundry"),
]


def create_demo(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    pwd = make_password(os.environ.get("DEMO_PASSWORD", "demo12345"))
    for username, role, name in DEMO:
        User.objects.get_or_create(
            username=username,
            defaults={"role": role, "first_name": name, "password": pwd},
        )


def remove_demo(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username__in=[d[0] for d in DEMO]).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.RunPython(create_demo, remove_demo)]
