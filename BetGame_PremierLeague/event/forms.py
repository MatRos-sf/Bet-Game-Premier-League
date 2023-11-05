from django import forms

from .models import Event, EventRequest


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "name",
            "start_date",
            "end_date",
            "description",
            "fee",
            "first_place",
            "second_place",
            "third_place",
        ]
