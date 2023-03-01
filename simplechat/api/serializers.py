from rest_framework import serializers
from .models import Thread, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')  # retrieve sender name

    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {
            'thread': {
                'write_only': True
            },
            'sender': {
                'write_only': True
            },
        }


class LastMessageSerializer(MessageSerializer):
    thread_link = serializers.SerializerMethodField(read_only=True)
    sender = serializers.ReadOnlyField(source='sender.username')  # retrieve sender name instead sender id

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created', 'is_read', 'thread_link']

    def get_thread_link(self, obj):
        """Return thread's url with interlocutor as urls kwarg."""
        owners = self.context.get('request').user

        # Exclude owner from queryset and get interlocutor
        queryset = obj.thread.participants.exclude(id=owners.id).first()
        serializer = serializers.HyperlinkedRelatedField(view_name='thread-detail',
                                                         lookup_field='username',
                                                         lookup_url_kwarg='username',
                                                         read_only=True)
        url = serializer.get_url(queryset,
                                 view_name='thread-detail',
                                 request=self.context.get('request'),
                                 format=self.context.get('format'))
        return url


class UnreadMessageSerializer(serializers.ModelSerializer):
    thread_link = serializers.HyperlinkedIdentityField(view_name='thread-detail', lookup_field='sender',
                                                       lookup_url_kwarg='username', source='thread')
    sender = serializers.ReadOnlyField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created', 'thread_link', 'is_read']
        extra_kwargs = {
            'is_read': {
                'write_only': True
            }
        }


class ThreadSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    interlocutor = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['messages', 'interlocutor', 'created', 'updated']

    def get_messages(self, obj):
        """Return list of messages."""

        queryset = obj.messages.order_by('-created')

        # Return an empty list of messages if they don't exist
        if not queryset.exists():
            return []

        # Return last message if action is list
        if self.context.get('view').action == 'list':
            messages = LastMessageSerializer(queryset.first(), context=self.context)
        else:
            messages = MessageSerializer(queryset, many=True)

        return messages.data

    def get_interlocutor(self, obj):
        """Return interlocutor username."""

        owners = self.context.get('request').user
        queryset = obj.participants.exclude(id=owners.id).first()
        return queryset.username
