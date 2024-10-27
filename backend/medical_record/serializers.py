from rest_framework import serializers
from .models import MedicalRecord

class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the main MedicalRecord model. This serializer will be used to create and retrieve the latest version.
    """
    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "user",
            "date",
            "doctor_name",
            "hospital_name",
            "hospital_address",
            "dynamic_diagnosis",
            "prescription",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at",]

    
class MedicalRecordHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the historical records of MedicalRecord using Django Simple History.
    """
    history_id = serializers.IntegerField()  # Unique ID for each historical entry
    history_date = serializers.DateTimeField()  # Date the change was made
    history_change_reason = serializers.CharField()  # Optional reason for the change
    history_user = serializers.StringRelatedField()  # User who made the change

    class Meta:
        model = MedicalRecord.history.model  # Access the historical model created by Simple History
        fields = [
            "id",
            "user",
            "date",
            "doctor_name",
            "hospital_name",
            "hospital_address",
            "dynamic_diagnosis",
            "prescription",
            "created_at",
            "updated_at",
            "history_id",
            "history_date",
            "history_change_reason",
            "history_user",
        ]
        read_only_fields = fields
