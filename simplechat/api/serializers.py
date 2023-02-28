from rest_framework import serializers
from .models import Thread, Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')

    class Meta:
        model = Message
        fields = '__all__'
        extra_kwargs = {
            'thread': {
                'write_only': True
            }
        }


class LastMessageSerializer(MessageSerializer):
    thread_link = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created', 'is_read', 'thread_link']

    def get_thread_link(self, obj):
        owners = self.context.get('request').user
        queryset = obj.thread.participants.exclude(id=owners.id).first()
        serializer = serializers.HyperlinkedRelatedField(view_name='thread',
                                                         lookup_field='username',
                                                         lookup_url_kwarg='username',
                                                         read_only=True)
        url = serializer.get_url(queryset,
                                 view_name='thread',
                                 request=self.context.get('request'),
                                 format=self.context.get('format'))
        return url


class UnreadMessageSerializer(MessageSerializer):
    thread_link = serializers.HyperlinkedIdentityField(view_name='thread', lookup_field='sender',
                                                       lookup_url_kwarg='username', source='thread')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created', 'thread_link']


class ThreadSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()
    interlocutor = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['message', 'interlocutor', 'created', 'updated']

    def get_message(self, obj):
        queryset = obj.messages.order_by('-created')
        if not queryset.exists():
            return []

        if self.context.get('view').action == 'list':
            queryset = queryset.first()
            messages = LastMessageSerializer(queryset, context=self.context)
        else:
            messages = MessageSerializer(queryset, many=True)

        return messages.data

    def get_interlocutor(self, obj):
        owners = self.context.get('request').user
        queryset = obj.participants.exclude(id=owners.id).first()
        return queryset.username
