from rest_framework import serializers
from .models import Chat, Message
from django.contrib.auth import get_user_model

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'doctor', 'patient', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.first_name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'sender_name', 'content', 'timestamp']


class ChatListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    lastMessage = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'name', 'lastMessage', 'time']

    def get_name(self, obj):
        # Get the name of the other user in the chat (either patient or doctor)
        request_user = self.context['request'].user
        if obj.doctor == request_user:
            other_user = obj.patient
        else:
            other_user = obj.doctor
        return f"{other_user.first_name.capitalize()} {other_user.last_name.capitalize()}"

    def get_lastMessage(self, obj):
        # Get the content of the latest message in the chat
        last_message = obj.messages.last()
        return last_message.content if last_message else None

    def get_time(self, obj):
        # Get the timestamp of the latest message in the chat
        last_message = obj.messages.last()
        return last_message.timestamp if last_message else None

class ChatMessageSerializer(serializers.ModelSerializer):
    sentByMe = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'timestamp', 'sentByMe']

    def get_sentByMe(self, obj):
        # Check if the message was sent by the current user
        return obj.sender == self.context['request'].user

    def to_representation(self, instance):
        # Customize the output format
        return {
            'id': instance.id,
            'message': instance.content,
            'timestamp': instance.timestamp,
            'sentByMe': self.get_sentByMe(instance),
        }
