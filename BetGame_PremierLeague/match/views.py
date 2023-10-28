from django.shortcuts import render
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Match, Matchweek
from league.models import TeamStats


class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = "match/match_detail.html"

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        match = context["match"]
        season, league = match.get_season_and_league()
        context["table"] = TeamStats.get_season_table(season=season.year, league=league)
        return context
