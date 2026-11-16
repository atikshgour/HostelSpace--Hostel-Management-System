import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_services', '0002_complaint_assigned_to_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessAllocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateField()),
                ('valid_until', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mess_name', models.CharField(max_length=100)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='mess_allocation', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['student_id', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valid_from', models.DateField()),
                ('valid_until', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(max_length=80)),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('allocation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coupons', to='student_services.messallocation')),
            ],
            options={
                'ordering': ['-valid_until', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='messallocation',
            constraint=models.CheckConstraint(condition=models.Q(('valid_until__gte', models.F('valid_from'))), name='mess_allocation_valid_dates'),
        ),
        migrations.AddConstraint(
            model_name='messallocation',
            constraint=models.CheckConstraint(condition=models.Q(('mess_name__regex', '^\\s*$'), _negated=True), name='mess_name_not_blank'),
        ),
        migrations.AddConstraint(
            model_name='coupon',
            constraint=models.CheckConstraint(condition=models.Q(('valid_until__gte', models.F('valid_from'))), name='mess_coupon_valid_dates'),
        ),
        migrations.AddConstraint(
            model_name='coupon',
            constraint=models.CheckConstraint(condition=models.Q(('code__regex', '^\\s*$'), _negated=True), name='mess_coupon_code_not_blank'),
        ),
        migrations.AddConstraint(
            model_name='coupon',
            constraint=models.UniqueConstraint(fields=('allocation', 'code'), name='mess_coupon_allocation_code_unique'),
        ),
    ]
