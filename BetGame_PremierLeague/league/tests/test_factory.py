from league.models import League, Season, Team, TeamStats
from django.test import TestCase, tag
from datetime import date

from league.factories.models_factory import (
    LeagueFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)


class LeagueFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(LeagueFactoryTest, cls).setUpClass()
        LeagueFactory()

    def test_should_create_league(self):
        league = League.objects.all()

        self.assertTrue(league.first())
        self.assertEquals(league.count(), 1)

    def test_set_default_field(self):
        league = League.objects.first()

        self.assertEquals(league.name, "Premier League")
        self.assertEquals(league.country, "test_country")


class SeasonFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SeasonFactoryTest, cls).setUpClass()
        SeasonFactory()

    def test_should_create_league(self):
        league = League.objects.all()

        self.assertTrue(league.first())
        self.assertEquals(league.count(), 1)

    def test_should_create_season(self):
        season = Season.objects.all()

        self.assertTrue(season.first())
        self.assertEquals(season.count(), 1)

    def test_set_default_field(self):
        season = Season.objects.first()

        self.assertIsInstance(season.start_date, date)


class TeamFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TeamFactoryTest, cls).setUpClass()
        TeamFactory()

    def test_should_create_model_team(self):
        team = Team.objects.all()
        self.assertTrue(team.first())
        self.assertEquals(team.count(), 1)


class TeamStatsFactoryTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TeamStatsFactoryTest, cls).setUpClass()
        TeamStatsFactory()

    def test_should_create_model_team(self):
        team = Team.objects.all()
        self.assertTrue(team.first())
        self.assertEquals(team.count(), 1)

    def test_should_create_model_season(self):
        team = Team.objects.all()
        self.assertTrue(team.first())
        self.assertEquals(team.count(), 1)

    def test_should_create_model_team_stats(self):
        ts = TeamStats.objects.all()
        self.assertTrue(ts.first())
        self.assertEquals(ts.count(), 1)
