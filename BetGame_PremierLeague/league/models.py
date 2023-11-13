from django.db import models
from django.db.models import (
    Avg,
    Sum,
    ExpressionWrapper,
    F,
    FloatField,
)
from django.db.models.functions import Cast
from django.urls import reverse


class League(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50)
    emblem = models.URLField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def current_season(self):
        pass


class Season(models.Model):
    fb_id = models.CharField(
        max_length=20, unique=True, help_text="Season id from football database."
    )
    start_date = models.DateField()
    end_date = models.DateField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    is_currently = models.BooleanField(default=True)

    def __str__(self):
        league = self.league.name
        return f"{league} {self.start_date}"

    class Meta:
        ordering = ["start_date"]

    @property
    def matchweek(self) -> int:
        """
        Return the number of currently matchweek
        """
        return self.current_season.filter(finished=False).first().matchweek

    @classmethod
    def get_currently_season(cls, league: str):
        try:
            c_s = cls.objects.get(league__name=league, is_currently=True)
        except cls.DoesNotExist:
            return None
        return c_s

    def get_winner(self):
        pass


class Team(models.Model):
    fb_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=5, blank=True, null=True)
    # TODO: will change name currently_league -> league
    currently_league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="teams", blank=True, null=True
    )
    # TODO delete
    last_league = models.ForeignKey(
        League,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="previous_season_teams",
    )

    crest = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    club_colours = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("league:team-detail", args=[self.pk])


class TeamStats(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="stats")
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    played = models.SmallIntegerField(default=0)
    won = models.SmallIntegerField(default=0)
    drawn = models.SmallIntegerField(default=0)
    lost = models.SmallIntegerField(default=0)
    goals_for = models.SmallIntegerField(default=0)
    goals_against = models.SmallIntegerField(default=0)

    points = models.SmallIntegerField(default=0)

    def __str__(self):
        season_date = self.season.start_date.strftime("%y")
        return f"{self.team.name} {season_date} {self.points}"

    @property
    def goal_difference(self) -> int:
        return int(self.goals_for) - int(self.goals_against)

    @classmethod
    def get_season_table(cls, league: str, season: int = None):
        # TODO ma szukać w League aktualny sezon

        return cls.objects.filter(
            season__start_date__year=season, season__league__name=league
        ).order_by("-points", "-goals_for", "team__name")

    @classmethod
    def get_season_so_far(cls, season: Season, first_team: Team):
        stats = cls.objects.filter(season=season, teameam=first_team)

        y = stats.annotate(
            avg_goals_scored=Avg(F("goals_for") / F("played")),
            avg_goals_conceded=ExpressionWrapper(
                Cast("goals_against", FloatField()) / Cast("played", FloatField()),
                output_field=FloatField(),
            ),
        )
        return stats.first()

    @classmethod
    def get_team_stats(cls, team: Team) -> dict:
        stats = cls.objects.filter(team=team).aggregate(
            played=Sum("played"),
            wins=Sum("won"),
            losses=Sum("lost"),
            goals=Sum("goals_for"),
            goals_conceded=Sum("goals_against"),
        )
        return stats

    def update_stats(self, team_goal: int, opponent_goal: int) -> None:
        """
        Upgrade stats according to give goals.
        :param team_goal: Goals self.team
        :param opponent_goal: goals opponent team
        """
        if team_goal > opponent_goal:
            self.points += 3
            self.won += 1
        elif team_goal == opponent_goal:
            self.points += 1
            self.drawn += 1
        elif team_goal < opponent_goal:
            self.lost += 1

        self.played += 1
        self.goals_for += team_goal
        self.goals_against += opponent_goal
        self.save()
