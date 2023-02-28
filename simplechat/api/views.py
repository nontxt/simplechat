from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.exceptions import NotFound
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, UnreadMessageSerializer


class UnreadMessageListAPIView(ListAPIView):
    queryset = Message.objects.filter(is_read=False)
    serializer_class = UnreadMessageSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(thread__participants=self.request.user).exclude(sender=self.request.user)
        return queryset


class ThreadViewSet(ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer

    def get_queryset(self, interlocutor=None):
        queryset = self.queryset.filter(participants=self.request.user)
        if interlocutor:
            queryset = queryset.filter(participants=interlocutor)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('username', NotFound)
        if self.request.user.username == username:
            raise NotFound
        interlocutor = get_object_or_404(User, username=username)
        queryset = self.filter_queryset(self.get_queryset(interlocutor))
        if queryset.count() == 0:
            thread = Thread.objects.create()
            thread.participants.set([self.request.user, interlocutor])
        else:
            thread = queryset.get()

        serializer = self.get_serializer(thread)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('username', NotFound)
        queryset = self.filter_queryset(self.get_queryset())
        instance = get_object_or_404(queryset, participants__username=username)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
