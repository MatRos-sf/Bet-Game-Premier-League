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

    fb_id = models.CharField(max_length=20, unique=True, help_text='Season id from football database.') #TODO fb_id
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

    fb_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=5, blank=True, null=True)

    currently_league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams')
    last_league = models.ForeignKey(League, blank=True, null=True, on_delete=models.CASCADE,
                                    related_name='previous_season_teams')

    crest = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    club_colours = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class TeamStats(models.Model):

    team = models.ForeignKey(Team, on_delete=models.CASCADE, releated_name='stats')
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

