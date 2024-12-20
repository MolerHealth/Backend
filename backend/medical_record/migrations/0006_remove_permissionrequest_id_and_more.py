# Generated by Django 5.1.2 on 2024-11-28 10:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_record', '0005_alter_historicalmedicalrecord_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permissionrequest',
            name='id',
        ),
        migrations.AlterField(
            model_name='permissionrequest',
            name='medical_record',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='permission_request', serialize=False, to='medical_record.medicalrecord'),
        ),
    ]
