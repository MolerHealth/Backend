from celery import shared_task
from django.core.mail import send_mail
from .models import User, OTP
from .utils import token_generator

@shared_task(serializer='json', name="send_activation_email_task")
def send_activation_email(user_id):
    try:
        user = User.objects.get(id=user_id)
        activation_code = token_generator()
        otp = OTP.objects.create(otp=activation_code, user=user)
        
        message = f"Hello {user.username},\n\nPlease use the following code to activate your account: {activation_code}"

        send_mail(
            subject="Activate your account",
            message=message,
            from_email="your_email@example.com",  # Replace with your actual sender email
            recipient_list=[user.email],
            fail_silently=False,
        )
    except User.DoesNotExist:
        # Log an error message or handle the exception as needed
        print("User not found.")
        # Optionally, return something or log the error
        return "User not found."
