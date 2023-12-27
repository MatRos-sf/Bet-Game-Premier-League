from django.urls import path, include

from .views import BetsListView, UserFinishedBetsListView, BetSeasonSummaryView

urlpatterns = [
    path("", BetsListView.as_view(), name="bet-home"),
    path("finished/", UserFinishedBetsListView.as_view(), name="bet-finished"),
    path("summary/", BetSeasonSummaryView.as_view(), name="bet-season-summary"),
]
