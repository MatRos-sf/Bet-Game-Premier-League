from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models import F


from .models import Bet
from users.models import UserScores


@receiver(post_save, sender=Bet)
def allocation_point_for_won_bet(sender, instance, **kwargs):
    if instance.is_won:
        UserScores.objects.create(
            profile=instance.user.profile,
            points=1,
            description=UserScores.render_description(1, f"WON bet {instance.pk}"),
        )
