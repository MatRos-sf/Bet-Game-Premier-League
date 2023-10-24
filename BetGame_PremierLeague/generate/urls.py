from django.urls import path

from . import views as v

urlpatterns = [
    path("league/", v.GenerateLeagueView.as_view(), name="generate-league"),
    path("team/", v.GenerateTeamsView.as_view(), name="generate-team"),
    path("season/", v.GenerateSeasonView.as_view(), name="generate-season"),
    path("team_stats/", v.GenerateTeamStatsView.as_view(), name="generate-team_stats"),
    path(
        "matchweek/<int:s>/<int:mw>/",
        v.GenerateMatchweekView.as_view(),
        name="generate-matchweek",
    ),
]
