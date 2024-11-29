from django.db import models
from backend.settings import AUTH_USER_MODEL
from simple_history.models import HistoricalRecords
from django.db.models import Q

class MedicalRecord(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField(auto_now=True)
    doctor_name = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=100)
    hospital_address = models.TextField()
    medical_history = models.JSONField(default=dict, blank=True)
    vitals = models.JSONField(default=dict, blank=True)
    current_visit_details = models.JSONField(default=dict, blank=True)
    treatment_plan = models.JSONField(default=dict, blank=True)
    referral_info = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Adding Django Simple History
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.user.username} - {self.date}'

class PermissionRequest(models.Model):
    doctor = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests_made")
    patient = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="requests_received")
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name="permission_requests")
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")], default="pending")
    request_date = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField(null=True, blank=True)
    edit_permission = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "medical_record"],
                condition=Q(status="pending"),
                name="unique_pending_request_per_doctor_and_record"
            )
        ]
