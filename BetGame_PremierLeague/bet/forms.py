from django import forms

from .models import Bet
from league.models import Season


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ["choice"]


class ChoseSeasonForm(forms.Form):
    SEASON_YEARS = Season.objects.values_list("start_date__year", flat=True).order_by()
    SEASON_CHOICE = [("all", "All")] + [(year, str(year)) for year in SEASON_YEARS]
    season = forms.ChoiceField(
        choices=SEASON_CHOICE, widget=forms.Select(attrs={"class": "selected"})
    )
