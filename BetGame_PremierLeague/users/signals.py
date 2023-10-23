from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import Profile, SeasonPoints
from league.models import Season


@receiver(post_save, sender=User)
def create_profile_and_season_points(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        seasons = Season.objects.filter(is_currently=True)

        if seasons.exists():
            for season in seasons:
                SeasonPoints.objects.create(profile=profile, seasons=season)


# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()