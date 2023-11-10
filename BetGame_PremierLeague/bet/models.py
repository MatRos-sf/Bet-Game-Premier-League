from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q
from typing import Dict

from match.models import Matchweek


class Bet(models.Model):
    choices = [
        ("none", "None"),
        ("home", "Home Team"),
        ("draw", "Draw"),
        ("away", "Away Team"),
    ]
    match = models.ForeignKey(
        "match.Match", related_name="bets", on_delete=models.CASCADE
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.CharField(max_length=20, choices=choices, default="none")
    risk = models.BooleanField(default=False)
    risk_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_won = models.BooleanField(blank=True, null=True)

    class Meta:
        unique_together = ("match", "user")

    # TODO kiedy is_active ma się zmieniać na false ( wtedy  kiedy rozpoczyna się kolejka)
    def check_bet(self):
        if isinstance(self.is_won, bool):
            return self.is_won
        won, _ = self.match.winner
        # TODO musi być is_active = False
        if isinstance(won, str):
            self.is_won = won == self.choice
            self.is_active = False
            self.save()
        return self.is_won

    def save(self, *args, **kwargs):
        super(Bet, self).save(*args, **kwargs)

        if self.risk and not self.risk_date:
            self.risk_date = timezone.now()
            self.save()

    @classmethod
    def get_stats_matchweek(cls, matchweek: Matchweek) -> Dict[str, str]:
        """
        Generals static about matchweek. The method return dict with keys:
            amt_bets: amount all bets in matchweek
            won: average won bets
            risk_win: amount of bets with risk
        """
        amt_won_risk_bet = Count("risk", filter=Q(is_won=True) & Q(risk=True))
        stats = cls.objects.filter(match__matchweek=matchweek).aggregate(
            amt_bets=Count("id"), won=Avg("is_won"), risk_win=amt_won_risk_bet
        )

        return stats

    @classmethod
    def get_stats_user(cls, user: User) -> Dict[str, str]:
        risk_bets = Count("id", filter=Q(risk=True))
        win_bets_risk = Count("id", filter=Q(is_won=True) & Q(risk=True))
        won_bets = Count("is_won", filter=Q(is_won=True))

        stats = cls.objects.filter(user=user).aggregate(
            amt_bets=Count("id"),
            win_rate=Avg("is_won"),
            won_bets=won_bets,
            risk_bets=risk_bets,
            won_bets_risk=win_bets_risk,
        )

        try:
            stats["win_rate_risk_bet"] = int(
                stats["won_bets_risk"] / stats["risk_bets"] * 100
            )
        except ZeroDivisionError:
            stats["win_rate_risk_bet"] = 0
        stats["win_rate"] = int(stats["win_rate"] * 100)

        return stats
