from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from django.urls import path
from .views import (RegistrationAPIView, 
                    VerifyEmailAPIView, 
                    ResendVerifyEmailAPIView, 
                    UserAPIView,
                    UserLogInAPIView)

urlpatterns = [
    # authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/register', RegistrationAPIView.as_view(), name='register'),
    path('auth/user/verify-email', VerifyEmailAPIView.as_view(), name='verify_email'),
    path('auth/user/resend-verify-email', ResendVerifyEmailAPIView.as_view(), name='resend_verify_email'),
    path('auth/user/login', UserLogInAPIView.as_view(), name='login'),

    path('user/me/', UserAPIView.as_view(), name='user'),

]