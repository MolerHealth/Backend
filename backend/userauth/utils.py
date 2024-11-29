# import send email function
from django.utils import timezone
import string
import random
from django.conf import settings
from .models import OTP
from django.core.mail import send_mail


def token_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def checkOTPExpiration(otp):
    """Check if the otp is expired or not"""
    if otp:
        now = timezone.now()
        time_difference = now - otp.created_at
        if time_difference.seconds > 300:
            return False
        else:
            return True
    else:
        return False
    
def send_activation_email(user):
    otp = token_generator()

    OTP.objects.create(user=user, otp=otp)

    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. It will expire in 5 minutes.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    # Send the email
    send_mail(subject, message, email_from, recipient_list)