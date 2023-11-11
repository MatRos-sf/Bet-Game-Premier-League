import datetime
from typing import Tuple, Optional
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import QuerySet, Q, Case, Value, When, CharField, F

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

    class Meta:
        ordering = ["start_date"]

    def save(self, *args, **kwargs):
        super(Matchweek, self).save(*args, **kwargs)

        # check all match finished
        if (
            self.finished
            and self.amt_matches != self.matches.filter(finished=True).count()
        ):
            self.finished = False
            self.save()
            raise ValidationError(
                "The finished field cannot be true unless all matches are finished"
            )

    def check_bet_user(self, pk):
        bet = self.bet_set.filter(user_id=pk)

        return bet.first().choice if bet.exists() else False

    def is_editable(self) -> bool:
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

    @property
    def score(self) -> Optional[str]:
        if self.finished:
            return f"{self.home_goals}:{self.away_goals}"
        return

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
        """
        League object
        """
        return self.matchweek.season.league

    @classmethod
    def get_last_match(cls):
        return cls.objects.filter(finished=True).order_by("-start_date").first()

    @classmethod
    def get_next_matches(cls) -> QuerySet:
        return cls.objects.filter(finished=False)

    @classmethod
    def get_form_guide_team(cls, team: Team, amt: int) -> QuerySet:
        """
        This method returns the information on the last team matches and adds a new field:
            w: it indicates whether it is an H (home) match or an A (away) match,
            result: it provides information about the match: W (won), L (lost), D (draw).
        """
        fg = cls.objects.filter(
            Q(finished=True), Q(home_team=team) | Q(away_team=team)
        ).order_by("-start_date")[:amt]
        where_played = Case(
            When(home_team=team, then=Value("H")),
            default=Value("A"),
            output_field=CharField(),
        )
        result = Case(
            When(home_goals=F("away_goals"), then=Value("D")),
            When(Q(home_goals__gt=F("away_goals")) & Q(w="H"), then=Value("W")),
            When(Q(home_goals__lt=F("away_goals")) & Q(w="A"), then=Value("W")),
            default=Value("L"),
            output_field=CharField(),
        )

        fg = fg.annotate(w=where_played, result=result)

        return fg

    def set_score(self, home_goals: int, away_goals: int) -> None:
        """
        Sets the score and checks all bets relate this match.
        """
        if not self.finished:
            self.home_goals = home_goals
            self.away_goals = away_goals
            self.finished = True
            self.save()

            bets = self.bets.all()

            for bet in bets:
                bet.check_bet()

    def get_absolute_url(self):
        return reverse("match-detail", kwargs={"pk": self.pk})

    def has_bet_for_match(self, user):
        return self.bet_set.filter(user=user).exists()

    def get_season_and_league(self) -> Tuple[datetime.date, str]:
        season = self.matchweek.season.start_date
        league = self.league
        return season, league

    def __str__(self):
        return self.score

    class Meta:
        ordering = ["start_date"]
