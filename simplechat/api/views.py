from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound

from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer, UnreadMessageSerializer
from .pagination import CustomPagination


def is_not_current_user(request, **kwargs):
    """Return User if exists and is not current user."""

    username = kwargs.get('username', NotFound)
    if request.user.username == username:
        raise NotFound
    return get_object_or_404(User, username=username)


class MessageListCreateAPIView(ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    pagination_class = CustomPagination
    thread = None  # Current thread

    def get_thread(self, interlocutor=None):
        """Return a thread for current user and interlocutor if exists."""

        user_threads = self.request.user.threads.all().values_list('id')
        self.thread = get_object_or_404(Thread, Q(id__in=user_threads) & Q(participants=interlocutor))
        return self.thread

    def get_queryset(self):
        """Return a queryset of messages for current user and interlocutor."""

        queryset = self.queryset.filter(thread=self.thread)
        return queryset

    def create(self, request, *args, **kwargs):
        """Create and return new message for current thread."""

        # Get interlocutor and current thread
        interlocutor = is_not_current_user(self.request, **kwargs)
        thread = self.get_thread(interlocutor=interlocutor)

        # Fill data for serializer
        data = request.data.copy()
        data['thread'] = thread.id
        data['sender'] = self.request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Update thread.updated after create message
        thread.update()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        """Return list of messages for current thread."""

        # Get interlocutor and current thread
        interlocutor = is_not_current_user(self.request, **kwargs)
        self.get_thread(interlocutor=interlocutor)

        # Original functionality
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UnreadMessageListCreateViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Message.objects.filter(is_read=False)
    serializer_class = UnreadMessageSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        """Return a queryset of unread messages for current user exclude himself messages."""

        queryset = self.queryset.filter(thread__participants=self.request.user).exclude(sender=self.request.user)
        return queryset

    @action(['POST'], detail=False)
    def mark_as_read(self, request, *args, **kwargs):
        """Mark a single or multiple messages as read."""

        # Get message_id from request.data and match this
        match request.data.get('message_id', None):
            case str() as messages_id:

                # If data contains alphabets return HTTP_400_BAD_REQUEST
                if not messages_id.isdigit():
                    return Response({'message_id': 'Must be single or list of digit'},
                                    status=status.HTTP_400_BAD_REQUEST)
                messages_id = [messages_id]
            case list() as messages_id:
                ...
            case _:

                # If message_id not provided return HTTP_400_BAD_REQUEST
                return Response({'message_id': 'Is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get messages witch provided in message_id
        messages = self.get_queryset().filter(id__in=messages_id)
        if not messages.exists():
            raise NotFound

        # Mark messages as read
        for message in messages:
            message.mark_as_read()
        return Response(status=status.HTTP_200_OK)


class ThreadModelViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    pagination_class = CustomPagination
    lookup_url_kwarg = 'username'

    def get_queryset(self, interlocutor=None):
        """Return a queryset of threads for current user and interlocutor (if exists)."""
        queryset = self.queryset.filter(participants=self.request.user)
        if interlocutor:
            queryset = queryset.filter(participants=interlocutor)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Return a thread with provided valid interlocutor or create and return them if it doesn't exist."""

        # Get interlocutor
        interlocutor = is_not_current_user(self.request, **kwargs)

        # Get thread, if not exist create them and return with HTTP_201_CREATED
        queryset = self.filter_queryset(self.get_queryset(interlocutor))
        if not queryset.exists():
            thread = Thread.objects.create()
            thread.participants.set([self.request.user, interlocutor])
            serializer = self.get_serializer(thread)
            return Response(serializer.data, status.HTTP_201_CREATED)

        # Get existed thread and return them with HTTP_200_OK
        thread = queryset.first()
        serializer = self.get_serializer(thread)
        return Response(serializer.data, status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Delete a thread if exists."""

        # Get interlocutor
        interlocutor = is_not_current_user(self.request, **kwargs)

        # Original functionality
        queryset = self.filter_queryset(self.get_queryset())
        instance = get_object_or_404(queryset, participants=interlocutor)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
