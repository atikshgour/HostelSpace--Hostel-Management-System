from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ('leave_attendance', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='deviation',
            constraint=models.UniqueConstraint(
                condition=Q(active=True),
                fields=('student', 'rule', 'remarks'),
                name='arin_unique_active_deviation_replay',
            ),
        ),
    ]
