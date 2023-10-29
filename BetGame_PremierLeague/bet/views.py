from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
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
        matches = Matchweek.objects.filter(finished=False).first()
        return matches.matches.filter(finished=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BetsListView, self).get_context_data(**kwargs)
        mw = context["matches"].first().matchweek
        matchweek_is_started = mw.is_editable
        context["is_started"] = matchweek_is_started
        finished_matches = Match.objects.filter(matchweek=mw, finished=True)
        context["finished_matches"] = finished_matches
        return context


@login_required
def set_bet(request, pk: int, choice: str):
    match = Match.objects.get(id=pk)

    if not match.matchweek.is_editable():
        messages.error(
            request,
            "You cannot change your bet because the matchweek has already started.",
        )
        # return redirect("bet-home")
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    bet, created = Bet.objects.get_or_create(user=request.user, match=match)

    if not created and bet.choice == choice:
        bet.choice = "none"
    else:
        bet.choice = choice

    bet.save(update_fields=["choice"])

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
