from django.urls import path, include

from .views import BetsListView, UserFinishedBetsListView

urlpatterns = [
    path("", BetsListView.as_view(), name="bet-home"),
    path("finished/", UserFinishedBetsListView.as_view(), name="bet-finished"),
]
