from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):

    match = models.OneToOneField('match.Match', on_delete=models.CASCADE)
    date_of_bet = models.DateTimeField(default=timezone.now)
    date_of_match = models.DateTimeField(blank=True, null=True)

    home_team = models.ManyToManyField(User)
    draw = models.ManyToManyField(User)
    away_team = models.ManyToManyField(User)

    def all_bet(self):
        pass
