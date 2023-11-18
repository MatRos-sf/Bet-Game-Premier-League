from factory.django import DjangoModelFactory
from factory import Sequence, Faker, SubFactory

from league.models import League, Season, Team, TeamStats


class LeagueFactory(DjangoModelFactory):
    class Meta:
        model = League

    name = Sequence(lambda n: f"test_name_{n}")
    country = "test_country"


class SeasonFactory(DjangoModelFactory):
    class Meta:
        model = Season

    fb_id = Sequence(lambda n: f"test_fb_id_{n}")
    start_date = Faker("date_time")
    end_date = Faker("date_time")
    league = SubFactory(LeagueFactory)


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    fb_id = Sequence(lambda n: f"fb_id_{n}")
    name = Sequence(lambda n: f"team_{n}")


class TeamStatsFactory(DjangoModelFactory):
    class Meta:
        model = TeamStats

    team = SubFactory(TeamFactory)
    season = SubFactory(SeasonFactory)
