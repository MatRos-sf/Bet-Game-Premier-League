from django.test import TestCase, tag
from django.utils import timezone
from datetime import timedelta

from .factories.models_factory import MatchweekFactory, MatchFactory
from league.tests.factories.models_factory import LeagueFactory, SeasonFactory
from league.models import League, Season, Team
from match.models import Match, Matchweek


@tag("matchweek-factory")
class MatchweekFactoryTest(TestCase):
    def test_create_factory(self):
        MatchweekFactory()
        self.assertEquals(League.objects.count(), 1)
        self.assertEquals(Season.objects.count(), 1)
        self.assertEquals(Matchweek.objects.count(), 1)

    def test_create_batch_factory_models_should_be_order_by_start_date(self):
        season = SeasonFactory()
        MatchweekFactory.create_batch(10, season=season)
        self.assertEquals(Matchweek.objects.count(), 10)

        start_date_first = Matchweek.objects.first().start_date
        start_date_last = Matchweek.objects.last().start_date

        self.assertTrue(start_date_first < start_date_last)

    def test_more_realistic_matchweek(self):
        season = SeasonFactory()

        date_today = timezone.now()
        for i in range(1, 11):
            if i == 10:
                MatchweekFactory(
                    start_date=date_today, end_date=date_today, season=season
                )
            else:
                MatchweekFactory(
                    start_date=date_today - timedelta(weeks=10 - i),
                    end_date=date_today - timedelta(weeks=10 - i),
                    finished=True,
                    season=season,
                )

        self.assertEquals(Matchweek.objects.count(), 10)
        self.assertEquals(Matchweek.objects.filter(finished=True).count(), 9)
        self.assertTrue(
            Matchweek.objects.filter(finished=False).first().start_date, date_today
        )


class MatchFactoryTest(TestCase):
    def test_create_factory(self):
        MatchFactory()
        self.assertEquals(League.objects.count(), 1)
        self.assertEquals(Season.objects.count(), 1)
        self.assertEquals(Matchweek.objects.count(), 1)
        self.assertEquals(Match.objects.count(), 1)
        self.assertEquals(Team.objects.count(), 2)

    def test_create_batch_factory_models_should_create_ten_matches(self):
        matchweek = MatchweekFactory()
        MatchFactory.create_batch(10, matchweek=matchweek)

        self.assertEquals(Match.objects.count(), 10)

    def test_should_none_goals_when_instance_created(self):
        MatchFactory()
        match = Match.objects.all().first()
        self.assertEquals(Match.objects.count(), 1)
        self.assertFalse(match.home_goals)
        self.assertFalse(match.away_goals)
