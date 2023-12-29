
from django.shortcuts import render
from rest_framework.views import APIView, status
from .serializers import RegistrationSerializer, UserSerializer, VerifyEmailSerializer, UserLogInAPIViewSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .models import User
from rest_framework import authentication
from rest_framework import permissions
from .tasks import send_activation_email
from .utils import checkOTPExpiration
from .models import OTP
from django.shortcuts import get_object_or_404
from .utils import token_generator
from django.contrib.auth import authenticate
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    
    def post(self, request):
        """ Register new user."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                "message": "User registered successfully!",
                "statusCode": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            send_activation_email.delay(user.id)  # Pass user's ID instead of the user object
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyEmailAPIView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer =  self.serializer_class(data=data)

        if serializer.is_valid():
            otp = serializer.validated_data.get('otp')
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
            else:
                response_data = {
                "message": "User does not exist! Please register.",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if OTP.objects.filter(otp=otp).exists():
                get_otp = OTP.objects.get(otp=otp)
            else:
                response_data = {
                "message": "Invalid OTP! Please try again.",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if checkOTPExpiration(get_otp):
                user.is_active = True
                user.is_verified = True
                user.save()
                get_otp.delete()
                response_data = {
                "message": "User verified successfully!",
                "statusCode": status.HTTP_200_OK,
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                get_otp.delete()
                response_data = {
                "message": "OTP expired!",
                "statusCode": status.HTTP_400_BAD_REQUEST,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class ResendVerifyEmailAPIView(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer =  self.serializer_class(data=data)

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
            "message": "User details fetched successfully!",
            "statusCode": status.HTTP_200_OK,
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        serializer = UserSerializer(self.get_object(), data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                "message": "User details updated successfully!",
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
            "statusCode": status.HTTP_200_OK,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class UserLogInAPIView(generics.CreateAPIView):
    serializer_class = UserLogInAPIViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            email = serializer.validated_data['email']  # 'username' is used by default by ObtainAuthToken
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







