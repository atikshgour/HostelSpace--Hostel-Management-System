from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("student_services", "0004_enforce_unique_success"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="paymentattempt",
            constraint=models.UniqueConstraint(
                condition=Q(status="Pending"),
                fields=("fee", "provider"),
                name="one_pending_attempt_per_fee_provider",
            ),
        ),
    ]
