from django.urls import path

from .views import MatchDetailView, ResultsSeasonListView, FixturesSeasonListView

app_name = "match"
urlpatterns = [
    path("<int:pk>/", MatchDetailView.as_view(), name="detail"),
    path("results/", ResultsSeasonListView.as_view(), name="results"),
    path("fixtures/", FixturesSeasonListView.as_view(), name="fixtures"),
]
