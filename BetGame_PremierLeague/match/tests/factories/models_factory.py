from django.utils import timezone
from factory.django import DjangoModelFactory
from factory import Sequence, Faker, SubFactory

from match.models import Matchweek, Match
from league.tests.factories.models_factory import SeasonFactory, TeamFactory


class MatchweekFactory(DjangoModelFactory):
    class Meta:
        model = Matchweek

    matchweek = Sequence(lambda n: n + 1)
    start_date = Faker("date_time")
    end_date = Faker("date_time")
    season = SubFactory(SeasonFactory)


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    home_team = SubFactory(TeamFactory)
    away_team = SubFactory(TeamFactory)

    start_date = Faker("date_time", tzinfo=timezone.utc)
    matchweek = SubFactory(MatchweekFactory)
