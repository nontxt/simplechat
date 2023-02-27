from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        interlocutor = get_object_or_404(User, username=kwargs.get('username', None))
        queryset = self.filter_queryset(self.get_queryset(interlocutor))
        if queryset.count() == 0:
            thread = Thread.objects.create()
            thread.participants.set([self.request.user, interlocutor])
        else:
            thread = queryset.get()

        serializer = self.get_serializer(thread)
        return Response(serializer.data)
