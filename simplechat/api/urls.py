from django.urls import path
from .views import ThreadModelViewSet, UnreadMessageListCreateAPIView, MessageListCreateAPIView

urlpatterns = [
    path('threads', ThreadModelViewSet.as_view({'get': 'list'}), name='thread-list'),
    path('threads/<str:username>', ThreadModelViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='thread'),
    path('messages/unread', UnreadMessageListCreateAPIView.as_view(), name='unread'),
    path('messages/<str:username>', MessageListCreateAPIView.as_view()),

]
