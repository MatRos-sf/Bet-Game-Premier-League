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
    template_name = "bet/home.html"

    def get_queryset(self):
        matches = Matchweek.objects.filter(finished=False)
        if matches:
            return matches.first().matches.filter(finished=False)
        return matches

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BetsListView, self).get_context_data(**kwargs)

        mw = context["matches"].first()

        # season ended
        if not mw:
            context["end_season"] = True
            return context

        mw = context["matches"].first().matchweek
        matchweek_is_started = True  # TODO release: mw.is_editable

        context["is_started"] = matchweek_is_started
        finished_matches = Match.objects.filter(matchweek=mw, finished=True)

        context["finished_matches"] = finished_matches

        return context

    def post(self, request, *args, **kwargs):
        """
        Method:
           1. Firstly, get or create bets.
           2. Secondly, assign a choice.
           3. Thirdly, check when the user presses risk. If yes, then check:
               * Enough points to play with risk.
               * Check if bet.risk is equal to False.
        """

        cd = request.POST
        choice, match_pk = cd.get("bet").split()
        risk = cd.get("risk", False)

        bet, _ = Bet.objects.get_or_create(
            match=Match.objects.get(pk=match_pk), user=request.user
        )

        bet.choice = choice
        if risk:
            if not bet.risk and self.request.user.profile.all_points - 1 >= 0:
                bet.risk = risk
            else:
                messages.info(
                    request,
                    "You don't have enough points or you have already checked this option.",
                )
                return self.get(request)

        bet.save()
        return self.get(request)


@login_required
def set_bet(request, pk: int, choice: str):
    match = Match.objects.get(id=pk)
    # TODO release:
    # if not match.matchweek.is_editable():
    #     messages.error(
    #         request,
    #         "You cannot change your bet because the matchweek has already started.",
    #     )
    #     # return redirect("bet-home")
    #     return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    bet, created = Bet.objects.get_or_create(user=request.user, match=match)

    if not created and bet.choice == choice:
        bet.choice = "none"
    else:
        bet.choice = choice

    bet.save(update_fields=["choice"])

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class UserFinishedBetsListView(LoginRequiredMixin, ListView):
    model = Bet
    template_name = "bet/user_finished_bets.html"
    paginate_by = 10

    def get_queryset(self):
        qs = self.model.objects.filter(
            user=self.request.user, is_active=False
        ).order_by("-match__start_date")
        return qs
