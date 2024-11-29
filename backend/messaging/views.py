from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        recipient_email = request.data.get('recipient_email')
        content = request.data.get('content')

        if not recipient_email or not content:
            return Response({"error": "Recipient email and content are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the recipient user by email
            recipient = User.objects.get(email=recipient_email)
        except User.DoesNotExist:
            return Response({"error": "Recipient with this email does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        # Restrict patient-to-patient messaging
        if sender.is_patient and recipient.is_patient:
            return Response({"error": "Patients cannot send messages to other patients."},
                            status=status.HTTP_403_FORBIDDEN)

        # Restrict doctor-to-doctor messaging (optional, if needed)
        if sender.is_doctor and recipient.is_doctor:
            return Response({"error": "Doctors cannot send messages to other doctors."},
                            status=status.HTTP_403_FORBIDDEN)

        # Save the message
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=content
        )

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
    

class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, sender_email=None):
        user = request.user

        # Base query: messages where the logged-in user is the recipient
        messages = Message.objects.filter(recipient=user)

        if sender_email:
            try:
                # Filter messages further by sender email
                sender = User.objects.get(email=sender_email)
                messages = messages.filter(sender=sender)
            except User.DoesNotExist:
                return Response({"error": "Sender with this email does not exist."},
                                status=status.HTTP_404_NOT_FOUND)

        # Serialize and return the messages
        serializer = MessageSerializer(messages.order_by('-timestamp'), many=True)
        return Response(serializer.data)


class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, recipient=request.user)
            message.is_read = True
            message.save()
            return Response({"detail": "Message marked as read."}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
