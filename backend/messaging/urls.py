from django.urls import path
from .views import SendMessageView, MessageListView, MarkAsReadView

urlpatterns = [
    path('messages/send/', SendMessageView.as_view(), name='send_message'),
    path('messages/', MessageListView.as_view(), name='list_messages'),
    path('messages/<str:sender_email>/', MessageListView.as_view(), name='list_messages_from_sender'),
    path('messages/read/<int:message_id>/', MarkAsReadView.as_view(), name='mark_as_read'),
]
