from django.urls import path, include

from . import views

app_name = "league"

urlpatterns = [
    # path("<int:pk>/", views.LeagueDetailView.as_view(), name="detail"),
    # path("season/", views.SeasonDetailView.as_view(), name="league-season-list"),
    # path(
    #     "season/<int:pkt>/",
    #     views.SeasonDetailView.as_view(),
    #     name="league-season-detail",
    # ),
    # path("team/", views.TeamListView.as_view(), name="league-team-list"),
    path("team/<int:pk>/", views.TeamDetailView.as_view(), name="team-detail"),
]
