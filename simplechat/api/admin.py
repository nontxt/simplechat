from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from .models import Thread, Message


class ThreadForm(forms.ModelForm):
    model = Thread

    def clean(self):
        """Make sure that the thread can not contain more than two participants."""

        cleaned_data = super().clean()
        if cleaned_data.get('participants').count() != 2:
            raise ValidationError('Thread must have exactly two participants')

        # Make sure that thread doesn't exist
        thread = self.model.objects.filter(participants=cleaned_data['participants'][0])
        thread = thread.filter(participants=cleaned_data['participants'][1])
        if thread.exists():
            raise ValidationError('Thread already exists')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    form = ThreadForm
    list_display = ('get_participant_names', 'created', 'updated')

    def get_participant_names(self, obj):
        """Representation Thread object on Admin site."""

        return 'Thread between ' + ' and '.join(participant.username for participant in obj.participants.all())

    get_participant_names.short_description = 'Participants'


admin.site.register(Message)
