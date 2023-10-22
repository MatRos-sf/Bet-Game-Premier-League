from django.db import models

class League(models.Model):

    name = models.CharField(max_length=100, unique=True)
    # https://pypi.org/project/django-countries/
    country = models.CharField(max_length=50)
    emblem = models.URLField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def current_season(self):
        pass



class Season(models.Model):

    start_date = models.DateField()
    end_date = models.DateField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    matchweek = models.PositiveIntegerField(default=1)

    is_currently = models.BooleanField(default=True)

    def __str__(self):
        league = self.league.name
        return f"{league} {self.start_date}"

    def get_winner(self):
        pass


class Team(models.Model):

    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=5, blank=True, null=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    crest = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    club_colours = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class TeamStats(models.Model):

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    played = models.SmallIntegerField(default=0)
    won = models.SmallIntegerField(default=0)
    drawn = models.SmallIntegerField(default=0)
    lost = models.SmallIntegerField(default=0)
    goals_for = models.SmallIntegerField(default=0)
    goals_against = models.SmallIntegerField(default=0)

    points = models.SmallIntegerField(default=0)
    #status

    @property
    def goal_difference(self):
        return int(self.goals_for) - int(self.goals_against)

