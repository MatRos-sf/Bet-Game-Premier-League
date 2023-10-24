from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.LeagueListView.as_view(), name="league-list"),
    path("<int:pk>/", views.LeagueDetailView.as_view(), name="league-detail"),
    path("<int:pk>/update/", views.LeagueUpdateView.as_view(), name="league-update"),
    path("season/", views.SeasonDetailView.as_view(), name="league-season-list"),
    path(
        "season/<int:pkt>/",
        views.SeasonDetailView.as_view(),
        name="league-season-detail",
    ),
    path(
        "season/<int:pk>/update/",
        views.SeasonUpdateView.as_view(),
        name="league-season-update",
    ),
    path("team/", views.TeamListView.as_view(), name="league-team-list"),
    path("team/<int:pk>/", views.TeamDetailView.as_view(), name="league-team-detail"),
    path(
        "team/<int:pk>/update/",
        views.TeamUpdateView.as_view(),
        name="league-team-update",
    ),
    path(
        "team_stats/", views.TeamStatsListView.as_view(), name="league-teamstats-list"
    ),
    path(
        "team_stats/<int:pk>/",
        views.TeamStatsDetailView.as_view(),
        name="league-teamstats-detail",
    ),
    path(
        "team_stats/<int:pk>/",
        views.TeamStatsUpdateView.as_view(),
        name="league-teamstats-update",
    ),
]
