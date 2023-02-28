from django.urls import path
from .views import ThreadViewSet, UnreadMessageListAPIView


urlpatterns = [
    path('threads', ThreadViewSet.as_view({'get': 'list'}), name='thread-list'),
    path('threads/<str:username>', ThreadViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='thread'),
    path('unread', UnreadMessageListAPIView.as_view(), name='unread'),
]
