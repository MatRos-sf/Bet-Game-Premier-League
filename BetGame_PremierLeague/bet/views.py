from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from match.models import Match, Matchweek
from .models import Bet


class BetsListView(LoginRequiredMixin, ListView):
    model = Match
    context_object_name = "matches"

    def get_template_names(self):
        obj = Matchweek.objects.all().first()
        # TODO 2 różne template
        if obj.status == "Now":
            return ["bet/home.html"]
        return ["bet/home.html"]

    def get_queryset(self):
        matches = Matchweek.objects.all().first()
        return matches.matches.all()


@login_required
def set_bet(request, pk: int, choice: str):
    match = Match.objects.get(id=pk)

    if not match.matchweek.is_editable():
        messages.error(
            request,
            "You cannot change your bet because the matchweek has already started.",
        )
        return redirect("bet-home")

    bet, created = Bet.objects.get_or_create(user=request.user, match=match)

    if not created and bet.choice == choice:
        bet.choice = "none"
    else:
        bet.choice = choice

    bet.save(update_fields=["choice"])

    return redirect("bet-home")
