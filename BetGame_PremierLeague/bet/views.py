from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Max
from django.contrib import messages
from django.db.models import QuerySet
from django.utils import timezone
from typing import Any
from match.models import Match, Matchweek
from .models import Bet, Dict


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

        if timezone.now().date() < match.matchweek.start_date:
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


class BetSeasonSummaryView(LoginRequiredMixin, ListView):
    model = Bet
    template_name = "bet/bet_season_summary.html"

    def get_queryset(self) -> QuerySet[Bet]:
        return Bet.objects.filter(
            match__matchweek__start_date__year=2023, is_active=False
        ).only("is_won", "risk", "choice", "is_won", "match__matchweek__matchweek")

    def __create_pie_chart(self, labels: list, values: list):
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    textinfo="label+percent",
                    insidetextorientation="radial",
                )
            ]
        )
        return fig

    def __create_bar_chart(self, labels: list, values: list):
        import plotly.graph_objects as go

        fig = go.Figure([go.Bar(x=labels, y=values)])

        return fig

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super(BetSeasonSummaryView, self).get_context_data(**kwargs)
        bet_list = context["object_list"]
        bets = bet_list.aggregate(
            amt_bet_risk=Count("risk", filter=Q(risk=True)),
            amt_bet=Count("pk"),
            win_bets=Count("is_won", filter=Q(is_won=True)),
            lose_bets=Count("is_won", filter=Q(is_won=False)),
            home_bet=Count("choice", filter=Q(choice="home")),
            away_bet=Count("choice", filter=Q(choice="away")),
            draw_bet=Count("choice", filter=Q(choice="draw")),
            none_bet=Count("choice", filter=Q(choice="none")),
            max_matchweeks=Max("match__matchweek__matchweek"),
        )

        print(bets["max_matchweeks"])
        # pie chart with kind of bets
        amt_bet = bets["amt_bet"]
        amt_bet_risk = bets["amt_bet_risk"]
        pie = self.__create_pie_chart(
            ["bets without risk", "risk bets"], [amt_bet - amt_bet_risk, amt_bet_risk]
        )
        context["chart_kind_of_bets"] = pie.to_html()

        # pie chart with win and loses
        pie = self.__create_pie_chart(
            ["won bets", "lost bets"], [bets["win_bets"], bets["lose_bets"]]
        )
        context["chart_won_lost"] = pie.to_html()

        # Bar Charts
        chart = self.__create_bar_chart(
            ["home", "draw", "away"],
            [bets["home_bet"], bets["draw_bet"], bets["away_bet"]],
        )
        context["chart_choiced"] = chart.to_html()

        # group bar chart
        import plotly.graph_objects as go

        list_of_matchweek = list(range(1, bets["max_matchweeks"] + 1))
        query_dict = {}
        for i in list_of_matchweek:
            filter_key = f"matchweek_{i}"
            query_dict[filter_key] = Count(
                "pk", filter=Q(match__matchweek__matchweek=i)
            )

        q = bet_list.aggregate(**query_dict)

        fig = go.Figure(
            data=[
                go.Bar(name="", x=list(q.keys()), y=list(q.values())),
                # go.Bar(name='LA Zoo', x=list_of_matchweek, y=[12, 18, 29])
            ]
        )
        # Change the bar mode
        # fig.update_layout(barmode='stack')
        context["chart_group"] = fig.to_html()
        return context
