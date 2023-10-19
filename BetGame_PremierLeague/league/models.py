from django.db import models

class League(models.Model):

    name = models.CharField(max_length=100)
    # https://pypi.org/project/django-countries/
    country = models.CharField(max_length=50)
    #level = models.PositiveSmallIntegerField(choices=)
    season = models.DateField()


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    shortcut = models.CharField(max_length=5)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    #crest = models.ImageField()

    def __str__(self):
        return f"{self.name}"
