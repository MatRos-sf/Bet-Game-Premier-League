from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

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

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date", None)
        end_date = cleaned_data["end_date"]
        if start_date:
            if start_date > end_date:
                raise ValidationError("Start Date cannot be great than End Date")
            elif start_date == end_date:
                raise ValidationError("The dates must be different.")

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]
        if timezone.now() > start_date:
            raise ValidationError("The start date of the event must be after today.")
        return start_date

    # def clean_fee(self):
    #     user_points = self.request.user.profile.all_points
    #     fee = self.cleaned_data['fee']
    #     if user_points - fee < 0:
    #         raise ValidationError("You don't have enough points to create event!")


class SearchUsernameForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Type the username and press Enter to send an invitation to the event."
            }
        ),
    )
