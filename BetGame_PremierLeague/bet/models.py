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
