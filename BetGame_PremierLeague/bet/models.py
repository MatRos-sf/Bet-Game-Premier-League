from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):

    match = models.OneToOneField('match.Match', on_delete=models.CASCADE)

    home_team = models.ManyToManyField(User, related_name='bet_home')
    draw = models.ManyToManyField(User, related_name='bet_draw')
    away_team = models.ManyToManyField(User, related_name='bet_away')

    def all_bet(self):
        pass
