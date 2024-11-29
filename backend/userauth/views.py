from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .utils import send_activation_email, checkOTPExpiration

from .models import User, OTP, Doctor, Patient
from .serializers import (
    RegistrationSerializer,
    VerifyEmailSerializer,
    ResendOTPSerializer,
    UserProfileSerializer,
    LoginSerializer,
    DoctorProfileSerializer,
    PatientProfileSerializer,
)


# Registration API View
class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send activation email with OTP (asynchronously)
            send_activation_email(user)
            return Response(
                {
                    "message": "User registered successfully!",
                    "statusCode": status.HTTP_201_CREATED,
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Verify Email API View
class VerifyEmailAPIView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Verify a user's email using an OTP."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')

            user = get_object_or_404(User, email=email)
            otp_instance = get_object_or_404(OTP, user=user, otp=otp)

            # Check OTP expiration
            if checkOTPExpiration(otp_instance):
                user.is_active = True
                user.save()
                otp_instance.delete()
                return Response(
                    {"message": "Email verified successfully!"},
                    status=status.HTTP_200_OK,
                )
            else:
                otp_instance.delete()
                return Response(
                    {"error": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Resend Verification Email API View
class ResendVerifyEmailAPIView(APIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Resend a verification email with a new OTP."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = get_object_or_404(User, email=email)

            if user.is_active:
                return Response(
                    {"message": "User already verified!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Resend the activation email
            send_activation_email.delay(user.id)
            return Response(
                {"message": "Verification email resent successfully!"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login API View
class UserLogInAPIView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Log in a user and return an authentication token."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(request, username=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {"token": token.key, "message": "Login successful!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Profile API View
class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        """Retrieve user details."""
        serializer = self.get_serializer(self.get_object())
        return Response(
            {
                "message": "User details fetched successfully!",
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        """Update user details."""
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User details updated successfully!",
                    "statusCode": status.HTTP_200_OK,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Delete a user account."""
        self.get_object().delete()
        return Response(
            {"message": "User deleted successfully!", "statusCode": status.HTTP_200_OK},
            status=status.HTTP_200_OK,
        )


# Doctor Profile API View
class DoctorProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Retrieve the profile of a doctor."""
        if not request.user.is_doctor:
            return Response(
                {"error": "You are not a doctor."},
                status=status.HTTP_403_FORBIDDEN,
            )

        doctor_profile = get_object_or_404(Doctor, user=request.user)
        serializer = DoctorProfileSerializer(doctor_profile)
        return Response(
            {"data": serializer.data, "message": "Doctor profile retrieved!"},
            status=status.HTTP_200_OK,
        )


# Patient Profile API View
class PatientProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Retrieve the profile of a patient."""
        if not request.user.is_patient:
            return Response(
                {"error": "You are not a patient."},
                status=status.HTTP_403_FORBIDDEN,
            )

        patient_profile = get_object_or_404(Patient, user=request.user)
        serializer = PatientProfileSerializer(patient_profile)
        return Response(
            {"data": serializer.data, "message": "Patient profile retrieved!"},
            status=status.HTTP_200_OK,
        )
