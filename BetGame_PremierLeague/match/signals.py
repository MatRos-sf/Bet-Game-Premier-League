from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db.models import F

from .models import Match, Matchweek
from bet.models import Bet
from league.models import Team, TeamStats, Season


@receiver(pre_save, sender=Match)
def match_change_status_finished(sender, instance: Match, **kwargs) -> None:
    """
    Prevents the 'finished' field from being changed once it is set to 'True'.
    """
    if instance.pk:
        match = Match.objects.get(pk=instance.pk)
        if match.finished and instance.finished == False:
            raise ValidationError(
                "The finished field cannot be changed once if it is set to true!"
            )


# @receiver(post_save, sender=Matchweek)
# def update_obj_season_when_add_new_matchweek(sender, instance, **kwargs):
#     season = instance.season
#     if season.matchweek < instance.matchweek:
#         season.matchweek = instance.matchweek
#         season.save(update_fields=["matchweek"])
#         # TODO zrobić kiedy koniec sezonu
#
#
# @receiver(post_save, sender=Match)
# def check_bets(sender, instance, **kwargs):
#     if instance.finished:
#         bets = Bet.objects.filter(match=instance)
#         for bet in bets:
#             bet.winner()
