from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Count, Q, Sum
from typing import Dict, List

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

    def __str__(self):
        return str(self.pk)

    def check_bet(self):
        if isinstance(self.is_won, bool):
            return self.is_won
        won, _ = self.match.winner
        if isinstance(won, str):
            self.is_won = won == self.choice
            self.is_active = False
            self.save()

            # notifications
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
            amt_bets=Count("id"),
            win_rate=Count("is_won", filter=Q(is_won=True)),
            risk_win=amt_won_risk_bet,
        )
        if stats["amt_bets"] > 0:
            stats["win_rate"] = int((stats["win_rate"] / stats["amt_bets"]) * 100)
        else:
            stats["win_rate"] = 0
        return stats

    @classmethod
    def get_stats_user(cls, user: User) -> Dict[str, str]:
        risk_bets = Count("id", filter=Q(risk=True) & Q(match__finished=True))
        win_bets_risk = Count("id", filter=Q(is_won=True) & Q(risk=True))
        won_bets = Count("is_won", filter=Q(is_won=True))

        stats = cls.objects.filter(user=user).aggregate(
            amt_bets=Count("id"),
            # win_rate=Avg("is_won", default=0),
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

        amt_bets = stats["amt_bets"]
        won_bets = stats["won_bets"]

        if amt_bets and won_bets:
            stats["win_rate"] = int(won_bets * 100 / amt_bets)
        else:
            stats["win_rate"] = 0

        # stats["win_rate"] = int(stats["win_rate"] * 100)

        return stats

    @classmethod
    def get_stats_season(
        cls, bets: Bet, matchweek_end: int
    ) -> Dict[str, List[str] | List[int]]:
        """
        Returns a dictionary with the following keys:
        - "matchweek": a list of matchweek numbers in ascending order.
        - "amt_bets": a list of the number of bets played in each corresponding matchweek.
          The list is ordered by matchweek, so amt_bets[0] corresponds to the 1st matchweek.

        :param matchweek_end: it is a last matchweek number
        :return: a dictionary containing "matchweek" and "amt_bets" lists.
        """
        list_of_matchweek = list(range(1, matchweek_end + 1))
        query_dict = {}

        for i in list_of_matchweek:
            filter_key = f"{i}"
            query_dict[filter_key] = Count(
                "pk", filter=Q(match__matchweek__matchweek=i)
            )

        dict_of_matchweeks_bet = bets.aggregate(**query_dict)

        stat_season = {
            "matchweek": list(dict_of_matchweeks_bet.keys()),
            "amt_bets": list(dict_of_matchweeks_bet.values()),
        }

        return stat_season
