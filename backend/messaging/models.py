
from django.db import models
from django.conf import settings

# Chat model to represent a chat session
class Chat(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='doctor_chats',
        limit_choices_to={'is_doctor': True}
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='patient_chats',
        limit_choices_to={'is_patient': True}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between Dr. {self.doctor.first_name} and {self.patient.first_name}"

# Message model for messages exchanged in a chat
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.first_name} at {self.timestamp}"
