from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Match
from bet.models import Bet


@receiver(post_save, sender=Match)
def create_bet(sender, instance, created, **kwargs):
    if created:
        Bet.objects.create(match=instance)

