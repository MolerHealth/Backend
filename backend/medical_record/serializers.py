from rest_framework import serializers
from .models import MedicalRecord, PermissionRequest
from userauth.models import User, Patient

class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for the main MedicalRecord model. This serializer will be used to create and retrieve the latest version.
    """
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ["created_at", "updated_at", "User"]

    
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
        fields = '__all__'
        read_only_fields = fields
        
        
class PermissionRequestSerializer(serializers.ModelSerializer):
    doctor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    patient = serializers.SlugRelatedField(
        slug_field='email',  # Use the patient's email directly
        queryset=User.objects.filter(is_patient=True)  # Query only users who are patients
    )
    medical_record = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord.objects.all()
    )

    class Meta:
        model = PermissionRequest
        fields = '__all__'
        read_only_fields = ["status", "request_date", "response_date"]

    def create(self, validated_data):
        # Ensure the doctor field is populated correctly with the User instance
        validated_data["doctor"] = validated_data["doctor"].doctor_profile.user
        return super().create(validated_data)


class PermissionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRequest
        fields = ["status"]

