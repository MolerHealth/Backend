# Generated by Django 5.1.2 on 2024-11-28 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_record', '0009_alter_permissionrequest_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissionrequest',
            name='edit_permission',
            field=models.BooleanField(default=False),
        ),
    ]