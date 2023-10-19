from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey('match.Match', on_delete=models.CASCADE)
    date_of_bet = models.DateTimeField(default=timezone.now)
    date_of_match = models.DateTimeField(blank=True, null=True)
