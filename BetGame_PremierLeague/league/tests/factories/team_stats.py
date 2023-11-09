from factory.django import DjangoModelFactory
import factory

from league.models import TeamStats


class TeamStatsFactory(DjangoModelFactory):
    class Meta:
        model = TeamStats

    team = "Test_team"
    season = "test_season"
