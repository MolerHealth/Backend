from django.urls import path
from .views import CreateChatView, MessageListView, SendMessageView, ChatListView

urlpatterns = [
    path('chats/', ChatListView.as_view(), name='chat-list'),
    path('chats/create/', CreateChatView.as_view(), name='create-chat'),
    path('messages/<int:chat_id>/', MessageListView.as_view(), name='message-list'),
    path('messages/send/', SendMessageView.as_view(), name='send-message'),
]
