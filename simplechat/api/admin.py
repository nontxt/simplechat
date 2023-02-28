from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from .models import Thread, Message

admin.site.register(Message)


class ThreadForm(forms.ModelForm):
    model = Thread

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('participants').count() != 2:
            raise ValidationError('Thread must have exactly two participants')
        thread = self.model.objects.filter(participants=cleaned_data['participants'][0])
        thread = thread.filter(participants=cleaned_data['participants'][1])
        if thread.exists():
            raise ValidationError('Thread already exists')


@admin.register(Thread)
class QuestionAdmin(admin.ModelAdmin):
    form = ThreadForm
