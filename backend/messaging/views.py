from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

# Create a new chat instance
class CreateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        patient_id = request.data.get('patient_id')

        if not (doctor_id and patient_id):
            return Response({'error': 'Doctor and Patient IDs are required.'}, status=400)

        chat, created = Chat.objects.get_or_create(
            doctor_id=doctor_id,
            patient_id=patient_id
        )

        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=201 if created else 200)

# Fetch all messages in a specific chat
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id).order_by('timestamp')

# Send a message
class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        chat_id = request.data.get('chat_id')
        content = request.data.get('content')

        if not (chat_id and content):
            return Response({'error': 'Chat ID and content are required.'}, status=400)

        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            return Response({'error': 'Chat not found.'}, status=404)

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            content=content
        )

        serializer = MessageSerializer(message)
        return Response(serializer.data, status=201)

# Fetch all chat sessions for the logged-in user
class ChatListView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_doctor:
            return Chat.objects.filter(doctor=user)
        elif user.is_patient:
            return Chat.objects.filter(patient=user)
        return Chat.objects.none()
