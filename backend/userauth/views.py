from django.shortcuts import render

from django.shortcuts import render
from rest_framework import generics
from .serializers import RegistrationSerializer, VerifyEmailSerializer, UserSerializer
from rest_framework.views import APIView, status
from rest_framework.response import Response
from .utils import send_activation_email
from .models import User, OTP
from .tokenizer import checkOTPExpiration
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                "message": "user registered successfully",
                "statusCode": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            send_activation_email.delay(user.id)  # Assuming you're using user ID now
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailAPIView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"message": "User does not exist! Please register account"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                get_otp = OTP.objects.get(otp=otp)
            except OTP.DoesNotExist:
                return Response({"message": "Incorrect OTP! Please enter correct OTP"},
                                status=status.HTTP_400_BAD_REQUEST)

            if checkOTPExpiration(get_otp):
                user.is_active = True
                user.is_verified = True
                user.save()
                get_otp.delete()
                return Response({"message": "User is verified successfully"},
                                status=status.HTTP_200_OK)
            else:
                get_otp.delete()
                return Response({"message": "OTP has expired"},
                                status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)\
            

class ResendVerifyEmailAPIView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            user = get_object_or_404(User, email=email)
            if user.is_verified:
                response_data = {
                    "message": "User already verified!",
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                send_activation_email.delay(user)
                response_data = {
                    "message": "OTP sent successfully!",
                    "statusCode": status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_object())
        response_data = {
            "message": "User details fetched successfully",
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_object(), data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "User details updated successfully",
                "statusCode": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        response_data = {
            "message": "User deleted successfully!",
            "statusCode": status.HTTP_200_OK
        }
        return Response(response_data, status=status.HTTP_200_OK)
