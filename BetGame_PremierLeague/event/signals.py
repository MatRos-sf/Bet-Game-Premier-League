from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Event


@receiver(post_save, sender=Event)
def add_owner_to_members(sender, instance, created, **kwargs):
    if created:
        instance.members.add(instance.owner)  # do save()
