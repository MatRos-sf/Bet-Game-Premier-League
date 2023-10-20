from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from typing import List

from .models import League, Team, Season, TeamStats
from .forms import TeamForm
from football_data.premier_league import PremierLeague

class LeagueListView(LoginRequiredMixin, ListView):
    model = League
    template_name = ''
    context_object_name = 'leagues/'
    #ordering = ['-season']


class LeagueDetailView(LoginRequiredMixin, DetailView):
    model = League
    template_name = "league/"


class LeagueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = League
    template_name = 'league/'
    fields = ['name', 'country', 'emblem']

    def test_func(self):
        return self.request.user.is_superuser()


class SeasonListView(LoginRequiredMixin, ListView):
    model = Season
    template_name = ''
    context_object_name = 'leagues/'


class SeasonDetailView(LoginRequiredMixin, DetailView):
    model = Season
    template_name = "league/"


class SeasonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Season
    template_name = 'league/'
    fields = ['start_date', 'end_date', 'league']

    def test_func(self):
        return self.request.user.is_superuser()


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = ''
    context_object_name = 'leagues/'


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "league/"


class TeamUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Team
    template_name = 'league/'
    fields = ['name', 'shortcut', 'league', 'crest']

    def test_func(self):
        return self.request.user.is_superuser()


class TeamStatsListView(LoginRequiredMixin, ListView):
    model = TeamStats
    template_name = ''
    context_object_name = 'leagues/'


class TeamStatsDetailView(LoginRequiredMixin, DetailView):
    model = TeamStats
    template_name = "league/"


class TeamStatsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TeamStats
    template_name = 'league/'
    fields = ['played', 'won', 'drawn', 'goals_for', 'goals_against', 'points']

    def test_func(self):
        return self.request.user.is_superuser()

class GenericLeagueView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request):

        pl = PremierLeague()
        league = pl.get_info_currently_league()

        obj, created = League.objects.get_or_create(**league)
        if created:

            return render(request, 'league/generic/league.html',
                          {'object': league}, status=201)
        return render(request, 'league/generic/league.html', {},
                      status=200)

    def test_func(self):
        return self.request.user.is_superuser


class GenericTeamsView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request):

        pl = PremierLeague()
        teams = pl.get_info_currently_teams_in_league()
        created_team: List[Team] | None = []
        league = League.objects.get(name='Premier League')
        queryset = League.objects.all()

        for team in teams:
            if queryset.filter(name=team['name']).exists():
                continue

            team['league'] = league
            form = TeamForm(data=team)
            if form.is_valid():
                obj = form.save()
                created_team.append(obj)

        return render(request, 'league/generate/team.html')

    def test_func(self):
        return self.request.user.is_superuser