from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone

from league.models import Team


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

    @property
    def results(self):
        if self.home_goals and self.away_goals:
            return f"{self.home_team.name:>5} {self.home_goals}:{self.away_goals} {self.away_team.name}"

        return f"{self.home_team.name:>5} : {self.away_team.name}"

    @property
    def winner(self) -> None | str:
        if not self.finished:
            return

        if self.home_goals > self.away_goals:
            return "home"
        elif self.home_team == self.away_team:
            return "draw"
        else:
            return "away"

    @property
    def league(self):
        return self.matchweek.season.league.name

    def has_bet_for_match(self, user):
        return self.bet_set.filter(user=user).exists()

    def winners_bet(self):
        pass

    def __str__(self):
        return f"{self.home_team.name: <50} : {self.away_team.name: >50}"
