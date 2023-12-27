from django import forms

from .models import Team, Season


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class ChoseSeasonForm(forms.Form):
    season = forms.ChoiceField(widget=forms.Select(attrs={"class": "selected"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        SEASON_YEARS = Season.objects.values_list(
            "start_date__year", flat=True
        ).order_by()
        SEASON_CHOICE = [("all", "All")] + [(year, str(year)) for year in SEASON_YEARS]
        self.fields["season"].choices = SEASON_CHOICE
