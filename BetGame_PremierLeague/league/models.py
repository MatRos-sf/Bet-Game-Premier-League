from django.db import models
from django.core.exceptions import ValidationError


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
    fb_id = models.CharField(
        max_length=20, unique=True, help_text="Season id from football database."
    )
    start_date = models.DateField()
    end_date = models.DateField()
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    matchweek = models.PositiveIntegerField(default=1)

    is_currently = models.BooleanField(default=True)

    def __str__(self):
        league = self.league.name
        return f"{league} {self.start_date}"

    @classmethod
    def get_currently_season(cls, league: str):
        return cls.objects.get(league__name=league, is_currently=True)

    # TODO sprawdzić coś nie działa kiedy próbuje generować sezon pisczy że str nie ma .year
    # def save(self, *args, **kwargs):
    #     start_year = self.start_date.year
    #     end_year = self.end_date.year
    #     league = self.league
    #
    #     if end_year - start_year != 1:
    #         raise ValidationError(
    #             "The different between end_data and start_date should equal 0"
    #         )
    #
    #     if Season.objects.filter(
    #         league=league, start_date__year=start_year, end_date__year=end_year
    #     ).exists():
    #         raise ValidationError(
    #             f"The league {league} already exists in these years ({start_year}-{end_year})."
    #         )
    #
    #     super(Season, self).save(*args, **kwargs)

    def get_winner(self):
        pass

    class Meta:
        ordering = ["start_date"]


class Team(models.Model):
    fb_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    shortcut = models.CharField(max_length=5, blank=True, null=True)

    currently_league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name="teams", blank=True, null=True
    )
    last_league = models.ForeignKey(
        League,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="previous_season_teams",
    )

    crest = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    club_colours = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class TeamStats(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="stats")
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    played = models.SmallIntegerField(default=0)
    won = models.SmallIntegerField(default=0)
    drawn = models.SmallIntegerField(default=0)
    lost = models.SmallIntegerField(default=0)
    goals_for = models.SmallIntegerField(default=0)
    goals_against = models.SmallIntegerField(default=0)

    points = models.SmallIntegerField(default=0)
    # status

    @property
    def goal_difference(self):
        return int(self.goals_for) - int(self.goals_against)

    def __str__(self):
        season_date = self.season.start_date.strftime("%y")
        return f"{self.team.name} {season_date} {self.points}"

    @classmethod
    def get_season_table(cls, season: int, league: str):
        return cls.objects.filter(
            season__start_date__year=season, season__league__name=league
        ).order_by("-points", "-goals_for", "team__name")
