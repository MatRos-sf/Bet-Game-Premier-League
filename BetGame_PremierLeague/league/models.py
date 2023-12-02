from django.db import models
from django.db.models import Avg, Sum, ExpressionWrapper, F, FloatField, Case, When, Q
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
        return self.season_set.filter(is_currently=True).first()


class Season(models.Model):
    fb_id = models.CharField(
        max_length=20, unique=True, help_text="Season id from football database."
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)

    is_currently = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        league = self.league.name
        return f"{league} {self.start_date.year}"

    @property
    def matchweek(self) -> int:
        """
        Return the number of currently matchweek
        """
        return self.current_season.filter(finished=False).first().matchweek

    @property
    def amt_matchweeks(self) -> int:
        """
        The method returns the total number of matchweeks in particular season
        """
        amt_teams = self.teamstats_set.count()
        return amt_teams * 2 - 2

    @classmethod
    def get_currently_season(cls, league: str):
        try:
            c_s = cls.objects.get(league__name=league, is_currently=True)
        except cls.DoesNotExist:
            return None
        return c_s


class Team(models.Model):
    fb_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=5, blank=True, null=True)

    crest = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    club_colours = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    def get_absolute_url(self):
        return reverse("league:team-detail", args=[self.pk])

    def currently_league(self) -> bool:
        """
        Method checks if team is currently league then returns True
        """
        return self.stats.filter(season__is_currently=True).exists()


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

    @property
    def get_position(self):
        table = TeamStats.get_season_table(
            self.season.league, self.season.start_date.year
        )
        p = list(table).index(self)
        return p + 1

    @classmethod
    def get_season_table(cls, league: str, season: int = None):
        return (
            cls.objects.filter(
                season__start_date__year=season, season__league__name=league
            )
            .select_related("season", "team")
            .order_by("-points", "-goals_for", "team__name")
        )

    @classmethod
    def get_season_so_far(cls, season: Season, first_team: Team):
        stats = cls.objects.filter(season=season, team=first_team)

        stats = stats.annotate(
            avg_goals_scored=ExpressionWrapper(
                Cast("goals_for", FloatField()) / Cast("played", FloatField()),
                output_field=FloatField(),
            ),
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
