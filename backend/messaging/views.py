from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, ChatListSerializer, ChatMessageSerializer

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
class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        try:
            # Fetch the chat by ID
            chat = Chat.objects.get(id=chat_id)

            # Determine the other user in the chat
            if chat.doctor == request.user:
                other_user = chat.patient
            elif chat.patient == request.user:
                other_user = chat.doctor
            else:
                return Response({"error": "You do not have access to this chat."}, status=status.HTTP_403_FORBIDDEN)

            # Fetch messages for the specific chat
            messages = Message.objects.filter(chat=chat).select_related('sender')

            # Serialize messages with context to access request user
            message_serializer = ChatMessageSerializer(messages, many=True, context={'request': request})

            # Prepare user data for response
            user_data = {
                'id': other_user.id,
                'name': f"{other_user.first_name.capitalize()} {other_user.last_name.capitalize()}",
            }

            return Response({
                'user': user_data,
                'chats': message_serializer.data,
            })
        
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)


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
class ChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all chats where the logged-in user is either a doctor or a patient
        chats = Chat.objects.filter(
            doctor=request.user
        ) | Chat.objects.filter(
            patient=request.user
        )
        
        # Serialize the chats with the custom serializer
        serializer = ChatListSerializer(chats, many=True, context={'request': request})
        return Response({"chats": serializer.data})
