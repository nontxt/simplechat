from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Thread(models.Model):
    participants = models.ManyToManyField(User, related_name='threads')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']

    def update(self):
        """Updating thread."""
        self.updated = timezone.now()
        self.save()


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Message from {self.sender}: {self.text}"

    def mark_as_read(self):
        """Marking message as read."""
        self.is_read = True
        self.save()
