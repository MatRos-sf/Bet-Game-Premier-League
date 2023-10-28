from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from typing import List
from http import HTTPStatus
from django.core.exceptions import FieldError

from league.models import League, Team, Season, TeamStats
from league.forms import TeamForm
from match.models import Matchweek, Match
from football_data.premier_league import PremierLeague


def generate(request):
    return render(request, "generate/set_database.html")


class GenerateLeagueView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    A class downloads information about the league and put it into our database.
    """

    def get(self, request):
        pl = PremierLeague()
        league = pl.get_info_currently_league()

        if not league:
            messages.error(
                "Something is wrong with the server. Please, try again for a moment."
            )
            return render(self.request, "generate/set_database.html", {})

        try:
            obj, created = League.objects.get_or_create(**league)
        except FieldError:
            messages.error(self.request, "The payload has incorrect data.")
            return render(
                self.request,
                "generate/set_database.html",
                {},
                status=HTTPStatus.BAD_REQUEST,
            )

        if created:
            messages.success(
                self.request, f"The {obj.name} has been successfully created"
            )
            return render(
                self.request,
                "generate/set_database.html",
                {"object": league},
                status=HTTPStatus.CREATED,
            )

        messages.error(self.request, f"The {obj.name} already exist.")

        return render(
            self.request, "generate/set_database.html", {}, status=HTTPStatus.OK
        )

    def test_func(self):
        return self.request.user.is_superuser


class GenerateTeamsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        name_league, teams = pl.get_info_currently_teams_in_league()
        created_team: List[Team] | None = []
        league = League.objects.filter(name=name_league)

        if not league.exsits():
            # League doesn't exist
            return render(request, "generate/", {})

        league = league.first()

        for team in teams:
            team["league"] = league
            form = TeamForm(data=team)
            if form.is_valid():
                obj = form.save()
                created_team.append(obj)

        return render(request, "generate/team.html")

    def test_func(self):
        return self.request.user.is_superuser


class GenerateSeasonView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        season = pl.get_info_current_season()
        id_form_fd = season.pop("id_form_fd")

        league = get_object_or_404(League, name=season.pop("league"))

        is_season = Season.objects.filter(id_form_fd=id_form_fd, league=league).exists()

        if is_season:
            # HERE CAN BE UPDATE
            return render(request, "league/generate/", {})

        season_obj = Season.objects.create(
            league=league, id_form_fd=id_form_fd, **season
        )

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser


class GenerateTeamStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        season, table = pl.get_current_standings()

        season = get_object_or_404(Season, id_from_fd=season)

        for t in table:
            id_team = t.pop("id_from_fd")

            team_obj = get_object_or_404(Team, id_from_fd=id_team)

            if TeamStats.objects.filter(team=team_obj, season=season).exists():
                continue  # or create update

            TeamStats.objects.create(team=team_obj, season=season, **t)

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser


class GenerateMatchweekView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, s, mw):
        season = s
        mw = mw
        pl = PremierLeague()

        matchweek, matches = pl.get_matchweek(mw, season)

        season = Season.objects.filter(start_date__year=season)

        if not season.exists():
            return render(request, "league/generate/", {})

        season = season.first()
        matchweek_obj = Matchweek.objects.create(
            season=season, matchweek=mw, **matchweek
        )

        for match in matches:
            home_team = Team.objects.get(id_from_fd=match.pop("home_team_id"))
            away_team = Team.objects.get(id_from_fd=match.pop("away_team_id"))
            Match.objects.create(
                matchweek=matchweek_obj,
                home_team=home_team,
                away_team=away_team,
                **match,
            )

        return render(request, "league/generate/", {}, status=201)

    def test_func(self):
        return self.request.user.is_superuser
