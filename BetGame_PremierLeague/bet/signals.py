from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models import F


from .models import Bet
from users.models import SeasonPoints


@receiver(post_save, sender=Bet)
def allocation_point_for_won_bet(sender, instance, **kwargs):
    # TODO bet should be is_active = False
    if instance.is_won == True:  #
        sp = SeasonPoints.objects.get(
            profile=instance.user.profile, season=instance.match.matchweek.season
        )
        sp.points = F("points") + 1
        sp.save()
