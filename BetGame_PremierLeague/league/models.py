from django.db import models

class League(models.Model):

    name = models.CharField(max_length=100)
    # https://pypi.org/project/django-countries/
    country = models.CharField(max_length=50)
    season = models.DateField()
    emblem = models.URLField(blank=True, null=True)


class Season(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    #status = models.Choices()


    def get_winner(self):
        pass


class Team(models.Model):

    name = models.CharField(max_length=100, unique=True)
    shortcut = models.CharField(max_length=5)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    crest = models.URLField()

    def __str__(self):
        return f"{self.name}"

class Team_Stats(models.Model):

    team = models.ForeignKey(League, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    played = models.SmallIntegerField(default=0)
    won = models.SmallIntegerField(default=0)
    drawn = models.SmallIntegerField(default=0)
    goals_for = models.SmallIntegerField(default=0)
    goals_against = models.SmallIntegerField(default=0)

    points = models.SmallIntegerField(default=0)
    #status

    @property
    def goal_difference(self):
        return int(self.goals_for) - int(self.goals_against)

