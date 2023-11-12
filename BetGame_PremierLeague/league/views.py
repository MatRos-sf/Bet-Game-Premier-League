from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from typing import List

from .models import League, Team, Season, TeamStats
from match.models import Match


# TODO: unlock
# class LeagueDetailView(LoginRequiredMixin, DetailView):
#     model = League
#     template_name = "league/detail.html"


# class SeasonDetailView(LoginRequiredMixin, DetailView):
#     model = Season
#     template_name = "league/"


# class TeamListView(LoginRequiredMixin, ListView):
#     model = Team
#     template_name = ""
#     context_object_name = "leagues/"


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "league/team_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        team = context["object"]

        stats = TeamStats.get_team_stats(team=team)
        context["stats"] = stats

        context["next_match"] = Match.get_next_match(team)
        context["last_match"] = Match.get_last_match(team)

        fans = team.fans.annotate(sum=Sum("points__points", default=0)).order_by(
            "-sum"
        )[:5]

        context["top_fans"] = fans

        return context
