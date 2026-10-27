import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplaintCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.SlugField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=80)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=2000)),
                ('status', models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')], default='Open', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='complaints', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='student_services.complaintcategory')),
            ],
            options={
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='ComplaintTransition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('old_status', models.CharField(blank=True, max_length=16)),
                ('new_status', models.CharField(choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')], max_length=16)),
                ('remarks', models.CharField(max_length=500)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='history', to='student_services.complaint')),
            ],
            options={
                'ordering': ['created_at', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='complaint',
            index=models.Index(fields=['student', '-created_at', '-id'], name='complaint_student_created'),
        ),
        migrations.AddConstraint(
            model_name='complaint',
            constraint=models.CheckConstraint(condition=models.Q(('description__regex', '^\\s*$'), _negated=True), name='complaint_description_not_blank'),
        ),
        migrations.AddConstraint(
            model_name='complaint',
            constraint=models.CheckConstraint(condition=models.Q(('room__regex', '^\\s*$'), _negated=True), name='complaint_room_not_blank'),
        ),
        migrations.AddConstraint(
            model_name='complaint',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['Open', 'In Progress', 'Resolved'])), name='complaint_valid_status'),
        ),
    ]
