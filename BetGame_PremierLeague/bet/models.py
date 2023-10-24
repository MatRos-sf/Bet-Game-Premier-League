from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Bet(models.Model):
    choices = [('home', 'Home Team'), ('draw', "Draw"), ('away', 'Away Team')]
    match = models.OneToOneField('match.Match', on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.CharField(max_length=20, choices=choices)

    # status

    def all_bet(self):
        pass

    class Meta:
        unique_together = ('match', 'user')