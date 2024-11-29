from rest_framework import serializers
from .models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'doctor', 'patient', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'sender_name', 'content', 'timestamp']
