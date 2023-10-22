from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from typing import List
from league.models import League, Team, Season, TeamStats
from league.forms import TeamForm
#from match.models import Matchweek, Match
from football_data.premier_league import PremierLeague


class GenerateLeagueView(LoginRequiredMixin, UserPassesTestMixin, View):

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


class GenerateTeamsView(LoginRequiredMixin, UserPassesTestMixin, View):

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


class GenerateSeasonView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request):

        pl = PremierLeague()
        season = pl.get_info_current_season()
        league = League.objects.get(name='Premier League')

        is_season = Season.objects.filter(start_date=season['start_date'],
                                          end_date=season['end_date'], league=league).exists()

        if is_season:
            return render(request, "league/generate/", {})

        season['league'] = league
        season_obj = Season.objects.create(**season)

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser


class GenerateTeamStatsView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request):

        pl = PremierLeague()
        season, table = pl.get_current_standings()

        season = Season.objects.filter(start_date=season['start_date'],
                                          end_date=season['end_date'])

        if not season.exists():
            return render(request, "league/generate/", {})

        season = season.first()

        for t in table:
            team = t.pop('team')
            team_obj = Team.objects.get(name=team)

            if TeamStats.objects.filter(team=team_obj, season=season).exists():
                continue

            TeamStats.objects.create(team=team_obj, season=season, **t)

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser

class GenerateMatchweekView(LoginRequiredMixin, UserPassesTestMixin, View):

    def get(self, request):

        season = self.kwargs['season'] if self.kwargs['season'] else None
        mw = self.kwargs['matchweek']
        pl = PremierLeague()

        matchweek, matches = pl.get_matchweek(mw, season)

        season = Season.objects.filter(start_date__year=matchweek['start_date'])

        if not season.exists():
            return render(request, "league/generate/", {})

        season = season.first()

        for t in table:
            team = t.pop('team')
            team_obj = Team.objects.get(name=team)

            if TeamStats.objects.filter(team=team_obj, season=season).exists():
                continue

            TeamStats.objects.create(team=team_obj, season=season, **t)

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser
