from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import (
    RegistrationAPIView,
    VerifyEmailAPIView,
    ResendVerifyEmailAPIView,
    UserAPIView,
    UserLogInAPIView,
    DoctorProfileAPIView,
    PatientProfileAPIView,
)

urlpatterns = [
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', RegistrationAPIView.as_view(), name='register'),
    path('user/verify-email/', VerifyEmailAPIView.as_view(), name='verify_email'),
    path('user/resend-verify-email/', ResendVerifyEmailAPIView.as_view(), name='resend_verify_email'),
    path('user/login/', UserLogInAPIView.as_view(), name='login'),
    path('user/me/', UserAPIView.as_view(), name='user'),
    
    # Additional profile endpoints
    path('user/me/doctor/', DoctorProfileAPIView.as_view(), name='doctor_profile'),
    path('user/me/patient/', PatientProfileAPIView.as_view(), name='patient_profile'),
]
