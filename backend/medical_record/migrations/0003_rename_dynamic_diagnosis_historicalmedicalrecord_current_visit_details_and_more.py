# Generated by Django 5.1.2 on 2024-10-30 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical_record', '0002_alter_historicalmedicalrecord_prescription_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalmedicalrecord',
            old_name='dynamic_diagnosis',
            new_name='current_visit_details',
        ),
        migrations.RenameField(
            model_name='historicalmedicalrecord',
            old_name='prescription',
            new_name='medical_history',
        ),
        migrations.RenameField(
            model_name='medicalrecord',
            old_name='dynamic_diagnosis',
            new_name='current_visit_details',
        ),
        migrations.RenameField(
            model_name='medicalrecord',
            old_name='prescription',
            new_name='medical_history',
        ),
        migrations.AddField(
            model_name='historicalmedicalrecord',
            name='referral_info',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='historicalmedicalrecord',
            name='treatment_plan',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='historicalmedicalrecord',
            name='vitals',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='referral_info',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='treatment_plan',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='medicalrecord',
            name='vitals',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
