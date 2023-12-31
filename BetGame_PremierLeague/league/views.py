from django.shortcuts import render
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from .models import Team, TeamStats, League
from match.models import Match


class LeagueDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        league = (
            League.objects.prefetch_related(
                "season_set",
                "season_set__teamstats_set",
                "season_set__teamstats_set__team",
            )
            .filter(name="Premier League")
            .first()
        )

        if not league:
            return render(request, "league/league_detail.html", {})
        currently_team = (
            league.season_set.filter(is_currently=True)
            .first()
            .teamstats_set.all()
            .order_by("team__name")
        )
        table = TeamStats.get_season_table(
            "Premier League", currently_team.first().season.start_date.year
        )
        return render(
            request,
            "league/league_detail.html",
            {"league": league, "currently_team": currently_team, "table": table},
        )


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "league/team_detail.html"

    def get_context_data(self, **kwargs):
        context = super(TeamDetailView, self).get_context_data(**kwargs)
        team = context["object"]

        stats = TeamStats.get_team_stats(team=team)
        context["stats"] = stats
        context["stats"]["clean_sheets"] = Match.get_clean_sheets(team)

        context["next_match"] = Match.get_next_match(team)
        context["last_match"] = Match.get_last_match(team)

        fans = team.fans.annotate(sum=Sum("points__points", default=0)).order_by(
            "-sum"
        )[:5]

        context["top_fans"] = fans

        return context
