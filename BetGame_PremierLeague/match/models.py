import datetime
from typing import Tuple
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


class Matchweek(models.Model):
    matchweek = models.SmallIntegerField(
        help_text=_("Matchweek number (from 1 to n)"),
        validators=[MinValueValidator(1, _("Matchweek number cannot be less than 1."))],
    )
    start_date = models.DateField()
    end_date = models.DateField()
    season = models.ForeignKey(
        "league.Season", on_delete=models.CASCADE, related_name="current_season"
    )
    canceled = models.BooleanField(default=False)

    finished = models.BooleanField(default=False)

    @property
    def status(self):
        """
        3 differents status: before, now, after
        """
        # TODO zastanowić się czy to jest potrzebne
        if self.canceled:
            return "Canceled"

        time_now = timezone.now().date()
        if self.start_date <= time_now <= self.end_date:
            return "Now"
        elif time_now <= self.start_date:
            return "Before"
        else:
            return "After"

    @property
    def amt_matches(self) -> int:
        return self.matches.all().count()

    def check_bet_user(self, pk):
        bet = self.bet_set.filter(user_id=pk)

        return bet.first().choice if bet.exists() else False

    def is_editable(self):
        now = timezone.now().date()
        return now < self.start_date

    def __str__(self):
        start = self.season.start_date.strftime("%y")
        return f"Matchweek {self.matchweek}/{start}"


class Match(models.Model):
    home_team = models.ForeignKey(
        "league.Team", on_delete=models.CASCADE, related_name="home"
    )
    away_team = models.ForeignKey(
        "league.Team", on_delete=models.CASCADE, related_name="away"
    )

    start_date = models.DateTimeField()
    matchweek = models.ForeignKey(
        Matchweek, on_delete=models.CASCADE, related_name="matches"
    )

    home_goals = models.SmallIntegerField(blank=True, null=True)
    away_goals = models.SmallIntegerField(blank=True, null=True)

    finished = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_date"]

    @property
    def results(self):
        if self.finished:
            return f"{self.home_team.name} {self.home_goals}:{self.away_goals} {self.away_team.name}"

        return f"{self.home_team.name} vs {self.away_team.name}"

    @property
    def winner(self) -> Tuple[None, None] | Tuple[str, object]:
        if not self.finished:
            return None, None

        if self.home_goals > self.away_goals:
            return "home", self.home_team
        elif self.home_team == self.away_team:
            return "draw", True
        else:
            return "away", self.away_team

    @property
    def league(self):
        return self.matchweek.season.league.name

    @classmethod
    def get_last_match(cls):
        return cls.objects.filter(finished=True).order_by("-start_date").first()

    @classmethod
    def get_next_matches(cls):
        return cls.objects.filter(finished=False)

    def has_bet_for_match(self, user):
        return self.bet_set.filter(user=user).exists()

    def winners_bet(self):
        pass

    def get_season_and_league(self) -> Tuple[datetime.date, str]:
        season = self.matchweek.season.start_date
        league = self.matchweek.season.league.name
        return season, league

    def __str__(self):
        return self.results
