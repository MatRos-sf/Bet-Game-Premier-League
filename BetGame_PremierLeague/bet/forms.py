from django import forms

from .models import Bet


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ["choice"]


class RiskForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ["risk"]
