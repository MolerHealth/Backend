# Generated by Django 5.1.2 on 2024-11-28 15:32

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_record', '0011_remove_permissionrequest_edit_permission'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='permissionrequest',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='permissionrequest',
            name='edit_permission',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='permissionrequest',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'pending')), fields=('doctor', 'medical_record'), name='unique_pending_request_per_doctor_and_record'),
        ),
    ]
