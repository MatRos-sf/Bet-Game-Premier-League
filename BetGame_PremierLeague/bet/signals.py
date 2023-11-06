from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from typing import Type

from .models import Bet
from users.models import UserScores


@receiver(post_save, sender=Bet)
def allocation_point_for_won_bet(sender, instance: Bet, **kwargs) -> None:
    """
    Give points if user win Bet
    """

    if instance.is_won:
        points = 4 if instance.risk else 1
        UserScores.objects.create(
            profile=instance.user.profile,
            points=points,
            description=UserScores.render_description(points, f"WON bet {instance.pk}"),
        )


@receiver(post_save, sender=Bet)
def capture_risk_bet(sender, instance: Bet, **kwargs) -> None:
    """
    The signal create UserScore when user click risk.
    """
    if instance.risk and not instance.risk_date:
        UserScores.objects.create(
            profile=instance.user.profile,
            points=-1,
            description=UserScores.render_description(-1, f"risk bet {instance.pk}"),
        )
