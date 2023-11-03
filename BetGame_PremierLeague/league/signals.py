from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import SeasonPoints, Profile
from .models import Season


@receiver(post_save, sender=Season)
def change_previous_season_status(sender, instance, created, **kwargs):
    """
    The signal change previous season field (if exists) to False and
    update all SeasonPoints current fields to False

    """
    if created:
        league = instance.league
        season = Season.objects.filter(league=league)

        if season.count() == 1:
            return

        season = season[2]
        season.is_currently = False
        season.save()

        SeasonPoints.objects.filter(name=season).update(current=False)


@receiver(post_save, sender=Season)
def create_season_points(sender, instance, created, **kwargs):
    """
    The signal create SeasonPoinds for all Profil
    """

    if created:
        profiles = Profile.objects.all()

        for profile in profiles:
            SeasonPoints.objects.create(profile=profile, season=instance)
