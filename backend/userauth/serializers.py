from rest_framework import serializers
from .models import User, OTP
import re


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'birth_date']
        extra_kwargs = {'password': {'write_only': True}}
        
    # def validate_username(self, value):
    #     if User.objects.filter(username=value).exists():
    #         raise serializers.ValidationError("Username already taken.")
    #     return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


    def validate(self, value):
        password = value.get('password')
        confirm_password = value.pop('confirm_password', None)

        if not password or not confirm_password:
            raise serializers.ValidationError("Both password and confirm password are required.")
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        if len(password) < 8:
            raise serializers.ValidationError("Password should be at least 8 characters long.")
        if not re.search("[a-z]", password):
            raise serializers.ValidationError("Password should include at least one lowercase letter.")
        if not re.search("[A-Z]", password):
            raise serializers.ValidationError("Password should include at least one uppercase letter.")
        if not re.search("[0-9]", password):
            raise serializers.ValidationError("Password should include at least one number.")
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
            raise serializers.ValidationError("Password should include at least one special character (!@#$%^&*(),.?\":{}|<>).")

        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)

        # Extract username, email, and password from validated_data
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)

        # Ensure that username, email, and password are provided
        if not username or not email or not password:
            raise serializers.ValidationError("Username, email, and password are required.")

        # Call create_user with username, email, password, and other extra fields
        user = User.objects.create_user(username, email, password, **validated_data)
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    class Meta:
        model = OTP
        fields = ['otp', 'email']


class ResendVerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        model = OTP
        fields = ['email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'profile_picture']
        read_only_fields = ('username', 'profile_picture')


class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['first_name', 'last_name', 'username', 'phone_number', 'profile_picture',]
            read_only_fields = ('email',)