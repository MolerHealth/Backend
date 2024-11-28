# Generated by Django 5.1.2 on 2024-10-31 19:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_record', '0003_rename_dynamic_diagnosis_historicalmedicalrecord_current_visit_details_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=20)),
                ('request_date', models.DateTimeField(auto_now_add=True)),
                ('response_date', models.DateTimeField(blank=True, null=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_made', to=settings.AUTH_USER_MODEL)),
                ('medical_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permission_requests', to='medical_record.medicalrecord')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]