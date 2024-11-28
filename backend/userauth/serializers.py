from rest_framework import serializers
from .models import User, OTP, Doctor, Patient


# Registration Serializer
class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'is_doctor', 'is_patient']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)

        if password and password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Ensure either `is_doctor` or `is_patient` is specified
        if not data.get('is_doctor') and not data.get('is_patient'):
            raise serializers.ValidationError("User must be either a doctor or a patient.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        
        # Create a related Doctor or Patient profile if applicable
        if user.is_doctor:
            Doctor.objects.create(user=user)
        elif user.is_patient:
            Patient.objects.create(user=user)
        
        return user


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


# Email Verification Serializer
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


# Resend OTP Serializer
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'bio', 'profile_picture']


# Doctor Profile Serializer
class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['specialty', 'years_of_experience', 'hospital', 'certifications', 'availability']


# Patient Profile Serializer
class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['medical_history', 'allergies', 'blood_group']
