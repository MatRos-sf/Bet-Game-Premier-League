from league.models import League, Season, Team, TeamStats
from django.test import TestCase, tag
from datetime import date

from .factories.models_factory import (
    LeagueFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)


@tag("league-factory")
class LeagueFactoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        LeagueFactory()

    def test_should_create_league(self):
        league = League.objects.all()

        self.assertTrue(league.first())
        self.assertEquals(league.count(), 1)

    def test_set_default_field(self):
        league = League.objects.first()

        self.assertEquals(league.name, "test_name_0")
        self.assertEquals(league.country, "test_country")


class SeasonFactoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

        self.assertEquals(
            (season.fb_id, season.league.name), ("test_fb_id_0", "test_name_1")
        )

        self.assertIsInstance(season.start_date, date)


class TeamFactoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        TeamFactory()

    def test_should_create_model_team(self):
        team = Team.objects.all()
        self.assertTrue(team.first())
        self.assertEquals(team.count(), 1)

    def test_should_set_default_field(self):
        team = Team.objects.first()

        self.assertEquals(team.fb_id, "fb_id_0")
        self.assertEquals(team.name, "team_0")


class TeamStatsFactoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_should_set_default_field(self):
        ts = TeamStats.objects.first()

        self.assertEquals(ts.team.fb_id, "fb_id_1")
        self.assertEquals(ts.season.fb_id, "test_fb_id_1")