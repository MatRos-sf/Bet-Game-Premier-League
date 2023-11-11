from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.contrib import messages
from .models import Match, Matchweek
from league.models import TeamStats, Team


class MatchDetailView(LoginRequiredMixin, DetailView):
    model = Match
    template_name = "match/match_detail.html"

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        match = context["match"]
        season, league = match.get_season_and_league()
        table = TeamStats.get_season_table(season=season.start_date.year, league=league)
        context["table"] = table
        # TODO takie staty jak tu: https://www.premierleague.com/match/93424

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

        return context


class ResultsSeasonListView(LoginRequiredMixin, ListView):
    model = Match
    template_name = "match/results.html"
    paginate_by = 10

    def get_queryset(self):
        name_team = self.request.GET.get("name_team", "")
        if name_team:
            queryset = self.model.objects.filter(
                Q(finished=True),
                Q(home_team__name__contains=name_team)
                | Q(away_team__name__contains=name_team),
            )
            if not queryset.exists():
                messages.info(self.request, f"The Team: {name_team} not found!")
                queryset = self.model.objects.filter(finished=True)
        else:
            queryset = self.model.objects.filter(finished=True)
        return queryset.order_by("-start_date")

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ResultsSeasonListView, self).get_context_data(*kwargs)

        # season
        match = context["object_list"].first()
        season_name = f"{match.matchweek.season.start_date.strftime('%Y')}/{match.matchweek.season.end_date.strftime('%y')}"
        context["season_name"] = season_name

        return context
