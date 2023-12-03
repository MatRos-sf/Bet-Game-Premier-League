from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import QuerySet
from django.utils import timezone

from match.models import Match, Matchweek
from .models import Bet


class BetsListView(LoginRequiredMixin, ListView):
    model = Match
    context_object_name = "matches"
    template_name = "bet/home.html"

    def get_queryset(self) -> QuerySet[Match]:
        matchweek = Matchweek.objects.filter(finished=False).first()
        if matchweek:
            return matchweek.matches.filter(finished=False).select_related(
                "home_team",
                "away_team",
                "matchweek",
                "matchweek__season",
                "matchweek__season__league",
            )
        return matchweek

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(BetsListView, self).get_context_data(**kwargs)

        matchweek = context["matches"]

        # season ended
        if not matchweek:
            context["end_season"] = True
            return context

        matchweek = context["matches"].first().matchweek
        context["matchweek"] = matchweek

        matchweek_is_started = timezone.now().date() <= matchweek.start_date

        context["is_started"] = matchweek_is_started
        finished_matches = Match.objects.filter(
            matchweek=matchweek, finished=True
        ).select_related("home_team", "away_team")

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

        match = (
            Match.objects.select_related("matchweek")
            .only("matchweek__season__start_date")
            .get(pk=match_pk)
        )

        if match.matchweek.start_date < timezone.now().date():
            bet, _ = Bet.objects.get_or_create(
                match=Match.objects.get(pk=match_pk), user=request.user
            )

            bet.choice = choice
            if risk:
                self._try_place_bet(request, risk, bet)
            bet.save()
        else:
            messages.info(
                request, "You cannot create bet because the matchweek has been started!"
            )
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
