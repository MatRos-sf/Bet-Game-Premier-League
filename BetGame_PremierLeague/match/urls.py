from django.urls import path

from .views import MatchDetailView, ResultsSeasonListView

urlpatterns = [
    path("<int:pk>/", MatchDetailView.as_view(), name="match-detail"),
    path("results/", ResultsSeasonListView.as_view(), name="match-season-results"),
]
