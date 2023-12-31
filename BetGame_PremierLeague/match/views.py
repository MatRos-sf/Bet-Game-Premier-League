from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib import messages
from .models import Match
from league.models import TeamStats
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def count_different(match, team) -> int:
    if match.home_team == team:
        return match.home_goals - match.away_goals
    return match.away_goals - match.home_goals


def find_biggest_win_and_worst_defeat(qs_match, main_team):
    biggest_win, worst_defeat = None, None
    score_win, score_defeat = 0, 0

    for match in qs_match:
        diff = count_different(match, main_team)
        if diff > score_win:
            score_win = diff
            biggest_win = match
        elif diff < score_defeat:
            score_defeat = diff
            worst_defeat = match

    return biggest_win, worst_defeat


class MatchDetailView(LoginRequiredMixin, DetailView):
    # model = Match
    template_name = "match/match_detail.html"
    queryset = Match.objects.select_related(
        "home_team",
        "away_team",
        "matchweek",
        "matchweek__season",
        "matchweek__season__league",
    )

    @staticmethod
    def __create_chart(bets: dict) -> str:
        fig = make_subplots(
            1,
            2,
            specs=[[{"type": "domain"}, {"type": "domain"}]],
            subplot_titles=["Bets Results", "Type of Bets"],
        )
        fig.add_trace(
            go.Pie(
                labels=["Won", "Lost"],
                values=[bets["won"], bets["lost"]],
                marker=dict(colors=["green", "#e23730"]),
                scalegroup="two",
            ),
            1,
            1,
        )
        fig.add_trace(
            go.Pie(
                labels=["Bets without risk", "Risk Bets"],
                values=[bets["normal_bet"], bets["risk"]],
                scalegroup="two",
                marker=dict(colors=["#ecc921", "black"]),
            ),
            1,
            2,
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
        )
        pie = fig.to_html()
        return pie

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        match = context["match"]
        if match.finished:
            bets = match.bets.all()
            bets = bets.aggregate(
                won=Count("is_won", filter=Q(is_won=True)),
                lost=Count("is_won", filter=Q(is_won=False)),
                normal_bet=Count("risk", filter=Q(risk=False)),
                risk=Count("risk", filter=Q(risk=True)),
            )
            if not all(value == 0 for value in bets.values()):
                context["chart"] = self.__create_chart(bets)

        season, league = match.get_season_and_league()
        table = TeamStats.get_season_table(season=season.start_date.year, league=league)
        context["table"] = table
        position_home = table.filter(team=match.home_team).first().get_position
        position_away = table.filter(team=match.away_team).first().get_position

        context["position"] = {"home": position_home, "away": position_away}

        # form guide
        home = Match.get_form_guide_team(match.home_team, 5)
        away = Match.get_form_guide_team(match.away_team, 5)
        context["form_guide"] = {"home": home, "away": away}

        # recent meetings
        recent_meetings = Match.get_recent_meetings(match.home_team, match.away_team)
        context["recent_meetings"] = recent_meetings

        # season so far
        so_far_home = TeamStats.get_season_so_far(season, match.home_team)
        so_far_away = TeamStats.get_season_so_far(season, match.away_team)

        context["so_far_home"] = so_far_home
        context["so_far_away"] = so_far_away

        # count biggest and worst match
        context["home"] = self.__find_biggest_win_and_worst_defeat(
            match.home_team, match.matchweek.season
        )

        context["away"] = self.__find_biggest_win_and_worst_defeat(
            match.away_team, match.matchweek.season
        )

        context["clean_sheets"] = {
            "home": Match.get_clean_sheets(match.home_team, match.matchweek.season),
            "away": Match.get_clean_sheets(match.away_team, match.matchweek.season),
        }

        return context

    def __find_biggest_win_and_worst_defeat(self, team, season):
        matches_so_far = Match.get_season_finished_matches(team, season)
        biggest_win_and_worst_defeat = find_biggest_win_and_worst_defeat(
            matches_so_far, team
        )
        return {
            "bw": biggest_win_and_worst_defeat[0],
            "wd": biggest_win_and_worst_defeat[1],
        }


class ResultsSeasonListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "match/match_list_view.html"
    paginate_by = 10

    def get_queryset(self):
        name_team = self.request.GET.get("name_team", "")
        if name_team:
            queryset = self.model.objects.filter(
                Q(finished=True),
                Q(home_team__name__icontains=name_team)
                | Q(away_team__name__icontains=name_team),
            )
            if not queryset.exists():
                messages.info(self.request, f"The Team: {name_team} not found!")
                queryset = self.model.objects.filter(finished=True)
        else:
            queryset = self.model.objects.filter(finished=True)

        return queryset.select_related("home_team", "away_team", "matchweek").order_by(
            "-start_date"
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ResultsSeasonListView, self).get_context_data(*kwargs)

        # season
        match = context["object_list"].first()
        if not match:
            return context
        season_name = f"{match.matchweek.season.start_date.strftime('%Y')}/{match.matchweek.season.end_date.strftime('%y')}"
        context["season_name"] = season_name

        context["title"] = "Results"
        return context


class FixturesSeasonListView(ResultsSeasonListView):
    extra_context = {"title": "Fixtures"}

    def get_queryset(self):
        name_team = self.request.GET.get("name_team", "")
        if name_team:
            queryset = self.model.objects.filter(
                Q(finished=False),
                Q(home_team__name__icontains=name_team)
                | Q(away_team__name__icontains=name_team),
            )
            if not queryset.exists():
                messages.info(self.request, f"The Team: {name_team} not found!")
                queryset = self.model.objects.filter(finished=False)
        else:
            queryset = self.model.objects.filter(finished=False)
        return queryset.select_related("home_team", "away_team", "matchweek")
