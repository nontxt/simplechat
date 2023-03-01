from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ThreadModelViewSet, UnreadMessageListCreateViewSet, MessageListCreateAPIView

router = SimpleRouter(trailing_slash=False)
router.register(r'threads', ThreadModelViewSet, basename='thread')
router.register(r'messages/unread', UnreadMessageListCreateViewSet, basename='unread')

urlpatterns = [
    path('', include(router.urls)),
    path('messages/<str:username>', MessageListCreateAPIView.as_view(), name='messages'),
]
