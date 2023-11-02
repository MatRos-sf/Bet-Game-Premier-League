from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Match, Matchweek
from league.models import TeamStats, Team


class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = "match/match_detail.html"

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        match = context["match"]
        season, league = match.get_season_and_league()
        table = TeamStats.get_season_table(season=season.year, league=league)
        context["table"] = table
        # TODO takie staty jak tu: https://www.premierleague.com/match/93424
        return context


class ResultsSeasonListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "match/results.html"

    def get_queryset(self):
        queryset = self.model.objects.filter(
            finished=True, matchweek__season__is_currently=True
        )
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ResultsSeasonListView, self).get_context_data(*kwargs)

        # season
        match = context["object_list"].first()
        season_name = f"{match.matchweek.season.start_date.strftime('%Y')}/{match.matchweek.season.end_date.strftime('%y')}"
        context["season_name"] = season_name

        return context
