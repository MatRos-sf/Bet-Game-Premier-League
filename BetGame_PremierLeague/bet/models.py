from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Bet(models.Model):
    choices = [
        ("none", "None"),
        ("home", "Home Team"),
        ("draw", "Draw"),
        ("away", "Away Team"),
    ]
    match = models.ForeignKey("match.Match", on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.CharField(max_length=20, choices=choices, default="none")

    is_active = models.BooleanField(default=True)
    is_won = models.BooleanField(blank=True, null=True)

    # TODO kiedy is_active ma się zmieniać na false ( wtedy  kiedy rozpoczyna się kolejka)
    def winner(self):
        if self.is_won:
            return self.is_won

        won, _ = self.match.winner
        # TODO musi być is_active = False
        if won:
            self.is_won = won == self.choice
            self.save(update_fields=["is_won"])
        return self.is_won

    class Meta:
        unique_together = ("match", "user")
