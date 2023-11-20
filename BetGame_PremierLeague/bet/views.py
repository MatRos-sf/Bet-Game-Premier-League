from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet

from match.models import Match, Matchweek
from .models import Bet


class BetsListView(LoginRequiredMixin, ListView):
    model = Match
    context_object_name = "matches"
    template_name = "bet/home.html"

    def get_queryset(self) -> QuerySet[Match]:
        matchweek = Matchweek.objects.filter(finished=False).first()
        if matchweek:
            # return matchweeks.first().matches.filter(finished=False)
            return matchweek.matches.filter(finished=False)
        return matchweek

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BetsListView, self).get_context_data(**kwargs)

        mw = context["matches"].first()

        # season ended
        if not mw:
            context["end_season"] = True
            return context

        mw = context["matches"].first().matchweek
        matchweek_is_started = True

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
            self._try_place_bet(request, risk, bet)
        bet.save()
        return self.get(request)

    def _try_place_bet(self, request, risk, bet):
        if not bet.risk and self.request.user.profile.all_points - 1 >= 0:
            bet.risk = risk
        else:
            messages.info(
                request,
                "You don't have enough points or you have already checked this option.",
            )
        self.get(request)


class UserFinishedBetsListView(LoginRequiredMixin, ListView):
    model = Bet
    template_name = "bet/user_finished_bets.html"
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Bet]:
        return (
            self.model.objects.filter(user=self.request.user, is_active=False)
            .prefetch_related("match", "match__away_team", "match__home_team")
            .order_by("-match__start_date")
        )
