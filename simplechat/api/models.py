from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Thread(models.Model):
    participants = models.ManyToManyField(User)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        participants = self.participants.all()
        return f"Thread between {participants[0]} and {participants[1]}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.thread}: {self.text}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
