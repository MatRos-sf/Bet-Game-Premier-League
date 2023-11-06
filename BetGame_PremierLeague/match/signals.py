from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from .models import Match


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
