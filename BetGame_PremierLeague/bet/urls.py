from django.urls import path, include

from .views import BetsListView, set_bet

urlpatterns = [
    path("", BetsListView.as_view(), name="bet-home"),
    path("set/<int:pk>/<str:choice>/", set_bet, name="bet-set"),
]
