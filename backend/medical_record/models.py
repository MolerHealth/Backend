from django.db import models
from backend.settings import AUTH_USER_MODEL
from simple_history.models import HistoricalRecords

class MedicalRecord(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField()
    doctor_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=100)
    hospital_address = models.TextField()
    dynamic_diagnosis = models.JSONField(default=dict, blank=True)
    prescription =models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Adding Django Simple History
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.user.username} - {self.date}'
