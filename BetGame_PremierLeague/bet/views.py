from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.forms import formset_factory

from match.models import Match, Matchweek
from .models import Bet
from django.contrib.auth.models import User
from django.views.generic.edit import ModelFormMixin
from .forms import BetForm


class BetsListView(ListView):
    model = Match
    template_name = "bet/home.html"
    context_object_name = "matches"

    def get(self, request, *args, **kwargs):
        bets = Bet.objects.filter(user=request.user, is_active=True)
        matchweek = Matchweek.objects.all().first()

        amt_matches = matchweek.amt_matches

        if amt_matches != bets.count():
            # TODO na sztywno klepane jest 10 meczy, sprawdzić czy istnieje taki mecz
            for match in matchweek.matches.all():
                Bet.objects.create(user=request.user, match=match, choice="none")

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        matches = Matchweek.objects.all().first()
        return matches.matches.all()


# def set_bet(request, pk: int, choice: str):
#     bet =
