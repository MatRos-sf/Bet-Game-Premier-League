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
    league = models.ForeignKey("league.League", on_delete=models.CASCADE)

    @property
    def status(self):
        '''
        3 differents status: before, now, after
        :return:
        '''
        pass


class Match(models.Model):
    home = models.ForeignKey('league.Team', on_delete=models.CASCADE)
    away = models.ForeignKey('league.Team', on_delete=models.CASCADE)

    start_date = models.DateTimeField()
    matchweek = models.ForeignKey(Matchweek, on_delete=models.CASCADE)

    home_goals = models.SmallIntegerField(blank=True, null=True)
    away_goals = models.SmallIntegerField(blank=True, null=True)

    @property
    def status(self):
        """
        before, now, end, cancel
        :return:
        """
        pass

    def results(self):

        if self.status == 'end':
            return f'{self.home.name:>5} {self.home_goals}:{self.away_goals} {self.away.name}'

        return self.status