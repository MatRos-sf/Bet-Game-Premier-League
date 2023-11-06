from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from typing import List
from http import HTTPStatus
from django.core.exceptions import FieldError
from django.contrib.auth.models import User

import random

from league.models import League, Team, Season, TeamStats
from league.forms import TeamForm
from match.models import Matchweek, Match
from football_data.premier_league import PremierLeague
from bet.models import Bet


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
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
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
        name_league, teams = pl.get_teams()

        if not name_league and not teams:
            messages.error(
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
            )
            return redirect("generate-home")

        created_team: List[Team] | None = []
        league = League.objects.filter(name=name_league)

        if not league.exists():
            messages.error(
                self.request,
                f"{name_league} does not exist. Please try creating the league first.",
            )
            return redirect("generate-home")

        league = league.first()

        for team in teams:
            fb_id = team.pop("fb_id")
            name = team.pop("name")

            exist = Team.objects.filter(
                currently_league=league, fb_id=fb_id, name=name
            ).exists()
            if not exist:
                team_instance = Team.objects.create(
                    currently_league=league, fb_id=fb_id, name=name, **team
                )
                created_team.append(team_instance)
        if created_team:
            messages.success(
                self.request,
                f"{len(created_team)} teams have been successfully created",
            )
            status = HTTPStatus.CREATED
        else:
            messages.info(self.request, "None of the teams was created!")
            status = HTTPStatus.OK

        # TODO nie mam nic zrobione jeżli istnieje np. powinien sprawdzać dzane czy są aktulane

        return render(self.request, "generate/set_database.html", {}, status=status)

    def test_func(self):
        return self.request.user.is_superuser


class GenerateSeasonView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        season = pl.get_info_current_season()
        fb_id = season.pop("fb_id")

        if not season:
            messages.error(
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
            )
            return render(self.request, "generate/set_database.html", {})

        league = get_object_or_404(League, name=season.pop("league"))

        is_season = Season.objects.filter(fb_id=fb_id, league=league).exists()

        if is_season:
            messages.info(self.request, f"The season {fb_id} already exist.")
            return render(
                self.request, "generate/set_database.html", {}, status=HTTPStatus.OK
            )

        Season.objects.create(league=league, fb_id=fb_id, **season)
        messages.success(
            self.request, f"Season ({fb_id}) has been successfully created! "
        )
        return render(
            self.request, "generate/set_database.html", {}, status=HTTPStatus.CREATED
        )

    def test_func(self):
        return self.request.user.is_superuser


class GenerateTeamStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        season, table = pl.get_current_standings()

        if not season and not table:
            messages.error(
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
            )
            return render(self.request, "generate/set_database.html", {})

        season = get_object_or_404(Season, fb_id=season)

        for t in table:
            fb_id = t.pop("fb_id")

            team_obj = get_object_or_404(Team, fb_id=fb_id)

            if TeamStats.objects.filter(team=team_obj, season=season).exists():
                continue

            TeamStats.objects.create(team=team_obj, season=season, **t)

        messages.success(
            self.request, f"Currently team Stats have been successfully added! "
        )

        return render(
            self.request, "generate/set_database.html", {}, status=HTTPStatus.CREATED
        )

    def test_func(self):
        return self.request.user.is_superuser


class GenerateMatchweekView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, s, mw):
        season = s
        mw = mw
        pl = PremierLeague()

        matchweek, matches = pl.get_matchweek(mw, season)

        if not matchweek and not matches:
            messages.error(
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
            )
            return render(self.request, "generate/set_database.html", {})

        season = Season.objects.filter(start_date__year=season)

        if not season.exists():
            messages.error(self.request, "Season does not exist!")
            return render(self.request, "generate/set_database.html", {})

        season = season.first()
        matchweek_obj = Matchweek.objects.create(
            season=season, matchweek=mw, **matchweek
        )

        for match in matches:
            home_team = Team.objects.get(fb_id=match.pop("home_team_id"))
            away_team = Team.objects.get(fb_id=match.pop("away_team_id"))
            Match.objects.create(
                matchweek=matchweek_obj,
                home_team=home_team,
                away_team=away_team,
                **match,
            )

        messages.success(
            self.request, f"Currently matchweek has been successfully added! "
        )
        return render(
            self.request, "generate/set_database.html", {}, status=HTTPStatus.CREATED
        )

    def test_func(self):
        return self.request.user.is_superuser


class UpdateCurrentlyMatchweekView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        pl = PremierLeague()
        season = Season.get_currently_season(pl.name_league)

        info, matches = pl.get_matches_result(
            mw=season.matchweek, year=season.start_date.year
        )

        if not info and not matches:
            messages.error(
                self.request,
                "Something is wrong with the server. Please, try again for a moment.",
            )
            return render(self.request, "generate/set_database.html", {})

        season_matches = Match.objects.filter(matchweek__season=season, finished=False)
        count = 0

        for match in matches:
            match_instance = season_matches.filter(
                home_team__fb_id=match["home_team_id"]
            ).first()

            if not match_instance:
                continue

            match_instance.home_goals = match["home_goals"]
            match_instance.away_goals = match["away_goals"]
            match_instance.finished = True
            match_instance.save(update_fields=["home_goals", "away_goals", "finished"])
            count += 1
        messages.info(self.request, f"Updated {count} matches!")
        return render(
            self.request, "generate/set_database.html", {}, status=HTTPStatus.CREATED
        )

    def test_func(self):
        return self.request.user.is_superuser


def generate_bet(request):
    all_users = User.objects.all()
    for user in all_users:
        matchweeks = Matchweek.objects.filter(finished=True)

        for matchweek in matchweeks:
            matches = matchweek.matches.all()

            for match in matches:
                bet = Bet.objects.create(
                    match=match,
                    user=user,
                    choice=random.choice(["home", "draw", "away"]),
                )

                bet.winner()
    return redirect("bet-home")


def update(request):
    matchweek = Matchweek.objects.filter(finished=False).first()

    pl = PremierLeague()
    list_of_matches = pl.update_score_matches(
        matchweek.matchweek, matchweek.matches.count()
    )
    for i in list_of_matches:
        print(i)

    return HttpResponse("Hello")
