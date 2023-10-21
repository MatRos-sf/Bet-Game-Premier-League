from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


class Matchweek(models.Model):

    matchweek = models.SmallIntegerField(
        help_text=_('Matchweek number (from 1 to n)'),
        validators=[MinValueValidator(1, _("Matchweek number cannot be less than 1."))]
    )
    start_date = models.DateField()
    end_date = models.DateField()
    season = models.ForeignKey("league.Season", on_delete=models.CASCADE)

    @property
    def status(self):
        '''
        3 differents status: before, now, after
        '''
        time_now = timezone.now()
        if self.start_date <= time_now <= self.end_date:
            return "Now"
        elif time_now <= self.start_date:
            return "Before"
        else:
            return "After"


class Match(models.Model):
    home_team = models.ForeignKey('league.Team', on_delete=models.CASCADE)
    away_team = models.ForeignKey('league.Team', on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    matchweek = models.ForeignKey(Matchweek, on_delete=models.CASCADE)

    home_goals = models.SmallIntegerField(blank=True, null=True)
    away_goals = models.SmallIntegerField(blank=True, null=True)


    def results(self):

        if self.home_goals and self.away_goals:
            return f'{self.home_team.name:>5} {self.home_goals}:{self.away_goals} {self.away_team.name}'

        return f'{self.home_team.name:>5} : {self.away_team.name}'

    def is_finished(self):
        # start_date += 45 + 10 + 15 + 45 + 10 + 10
        pass