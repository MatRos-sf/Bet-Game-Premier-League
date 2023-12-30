from django import forms

from .models import Season, Team


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class ChoseSeasonForm(forms.Form):
    season = forms.ChoiceField(widget=forms.Select(attrs={"class": "selected"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        season_years = Season.objects.values_list(
            "start_date__year", flat=True
        ).order_by()
        season_choice = [("all", "All")] + [(year, str(year)) for year in season_years]
        self.fields["season"].choices = season_choice
