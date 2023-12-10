from django.test import TestCase, tag
from django.utils import timezone
from datetime import timedelta
from parameterized import parameterized
from django.urls import reverse
from django.contrib.auth.models import User

from league.factories.models_factory import (
    LeagueFactory,
    SeasonFactory,
    TeamFactory,
    TeamStatsFactory,
)
from match.factories.models_factory import MatchweekFactory, MatchFactory
from users.factories import UserFactory, UserScoresFactory
from league.models import League, Season, Team, TeamStats
from bet.factories.model_factory import BetFactory
from event.factories.models_factory import EventFactory


class SimpleDB(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        * Creat 3 different Users
        * Create 2 Events:
            1st:
                Started: 1st Matchweek and end the same time
                Fee: 3
                Members: 3
                Price: 60/25/15

        * 4 teams in Season
            resulted Match:
            team_0 0-3 team_1       team_2 5-1 team_3
            team_0 0-1 team_2       team_1 0-1 team_3
            team_3 4-1 team_0       team_1 1-1 team_2

            team_0 - team_3         team_2 - team_1
            team_2 - team_0         team_3 - team_1
            team_1 - team_0         team_3 - team_2

        +-------+--------+--------------+--------+-------+--------+---------------+-----------
        | Place | team   | played | Won | drawn | lost | goals_for | goals_against | points |
        +------+---------+-------+------+--------+-------+--------+---------------+----------
        |   1  | team_2  |    3  |   2  |   1   |   0  |       7   |       2       |   7   |
        |   2  | team_3  |    3  |   2  |   0   |   1  |       6   |       6       |   6   |
        |   3  | team_1  |    3  |   1  |   1   |   1  |       4   |       2       |   4   |
        |   4  | team_0  |    3  |   0  |   0   |   3  |       1   |       8       |   0   |
        +------+---------+--------------+--------+-------+--------+---------------+---------

        * bets:
            team_0 0-3 team_1:
                user_one = 'home'
                user_two = 'draw'
                user_three = 'away'     +1
            team_2 5-1 team_3:
                user_one = 'home'       +1
                user_two = 'draw'
                user_three = 'away'
            team_0 0-1 team_2:
                user_one = 'home' + risk        -1
                user_two = 'draw' + risk        -1
                user_three = 'away' + risk      +4

        """
        # Create Users
        UserFactory.create_batch(3)
        user_one, user_two, user_three = User.objects.all()[:3]

        # Add 10 points
        for user in (user_one, user_two, user_three):
            UserScoresFactory(profile=user.profile, points=10, description="test")
        # create League
        league = LeagueFactory()

        # season
        today = timezone.now()
        season = SeasonFactory(
            start_date=today - timedelta(weeks=3),
            end_date=today + timedelta(weeks=2),
            league=league,
            is_currently=True,
        )

        # 6 Teams
        team_0 = TeamFactory(name="team_0")
        team_1 = TeamFactory(name="team_1")
        team_2 = TeamFactory(name="team_2")
        team_3 = TeamFactory(name="team_3")

        # 6 Matchweeks:
        # first matchweek: team_0 0-3 team_1       team_2 5-1 team_3
        # bets
        # events
        start_end_date = today - timedelta(weeks=3)
        event = EventFactory(
            name="First event test",
            owner=user_one,
            start_date=start_end_date,
            end_date=start_end_date + timedelta(days=1),
            fee=3,
            first_place=60,
            second_place=25,
            third_place=15,
        )
        event.members.add(user_two, user_three)
        event.save()

        mw = MatchweekFactory(
            matchweek=1,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        match = MatchFactory(
            home_team=team_0,
            away_team=team_1,
            start_date=start_end_date,
            matchweek=mw,
        )

        for user, choice in zip(
            [user_one, user_two, user_three], ["home", "draw", "away"]
        ):
            BetFactory(match=match, user=user, choice=choice)
        match.set_score(home_goals=0, away_goals=3)

        match = MatchFactory(
            home_team=team_2, away_team=team_3, start_date=start_end_date, matchweek=mw
        )

        for user, choice in zip(
            [user_one, user_two, user_three], ["home", "draw", "away"]
        ):
            BetFactory(match=match, user=user, choice=choice)
        match.set_score(home_goals=5, away_goals=1)

        mw.finished = True
        mw.save()

        # second matchweek: team_0 0-1 team_2       team_1 0-1 team_3
        start_end_date = today - timedelta(weeks=2)
        mw = MatchweekFactory(
            matchweek=2,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        match = MatchFactory(
            home_team=team_0,
            away_team=team_2,
            start_date=start_end_date,
            matchweek=mw,
        )
        for user, choice in zip(
            [user_one, user_two, user_three], ["home", "draw", "away"]
        ):
            BetFactory(match=match, user=user, choice=choice, risk=True)
        match.set_score(home_goals=0, away_goals=1)

        MatchFactory(
            home_team=team_1,
            away_team=team_3,
            start_date=start_end_date,
            matchweek=mw,
            home_goals=0,
            away_goals=1,
            finished=True,
        )
        mw.finished = True
        mw.save()

        # third matchweek: team_3 4-1 team_0       team_1 1-1 team_2
        start_end_date = today - timedelta(weeks=1)
        mw = MatchweekFactory(
            matchweek=3,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        MatchFactory(
            home_team=team_3,
            away_team=team_0,
            start_date=start_end_date,
            matchweek=mw,
            home_goals=4,
            away_goals=1,
            finished=True,
        )
        MatchFactory(
            home_team=team_1,
            away_team=team_2,
            start_date=start_end_date,
            matchweek=mw,
            home_goals=1,
            away_goals=1,
            finished=True,
        )
        mw.finished = True
        mw.save()

        # fourth matchweek: team_0 - team_3         team_2 - team_1
        start_end_date = today
        mw = MatchweekFactory(
            matchweek=4,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        MatchFactory(
            home_team=team_0, away_team=team_3, start_date=start_end_date, matchweek=mw
        )
        MatchFactory(
            home_team=team_2, away_team=team_1, start_date=start_end_date, matchweek=mw
        )

        # fifth matchweek: team_2 - team_0         team_3 - team_1
        start_end_date = today + timedelta(weeks=1)
        mw = MatchweekFactory(
            matchweek=5,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        MatchFactory(
            home_team=team_2, away_team=team_0, start_date=start_end_date, matchweek=mw
        )
        MatchFactory(
            home_team=team_3, away_team=team_1, start_date=start_end_date, matchweek=mw
        )

        # sixth matchweek: team_1 - team_0         team_3 - team_2
        start_end_date = today + timedelta(weeks=2)
        mw = MatchweekFactory(
            matchweek=6,
            start_date=start_end_date,
            end_date=start_end_date,
            season=season,
        )
        MatchFactory(
            home_team=team_1, away_team=team_0, start_date=start_end_date, matchweek=mw
        )
        MatchFactory(
            home_team=team_3, away_team=team_2, start_date=start_end_date, matchweek=mw
        )

        # TeamStats
        TeamStatsFactory(
            team=team_0,
            season=season,
            played=3,
            won=0,
            drawn=0,
            lost=3,
            goals_for=1,
            goals_against=8,
            points=0,
        )
        TeamStatsFactory(
            team=team_1,
            season=season,
            played=3,
            won=1,
            drawn=1,
            lost=1,
            goals_for=4,
            goals_against=2,
            points=4,
        )
        TeamStatsFactory(
            team=team_2,
            season=season,
            played=3,
            won=2,
            drawn=1,
            lost=0,
            goals_for=7,
            goals_against=2,
            points=7,
        )
        TeamStatsFactory(
            team=team_3,
            season=season,
            played=3,
            won=2,
            drawn=0,
            lost=1,
            goals_for=6,
            goals_against=6,
            points=6,
        )


@tag("league")
class LeagueTest(SimpleDB):
    def test_object_name(self):
        league = League.objects.first()
        self.assertEquals(str(league), league.name)

    def test_should_create_one_league(self):
        expected_name = "Premier League"

        self.assertEquals(League.objects.count(), 1)
        self.assertEquals(League.objects.first().name, expected_name)

    def test_should_return_currently_season_if_exists(self):
        league = League.objects.first()
        season = Season.objects.first()

        self.assertEquals(league.current_season(), season)


class SeasonTests(SimpleDB):
    def test_season_name(self):
        start_date = timezone.now() - timedelta(weeks=3)
        expected_name = f"Premier League {start_date.year}"
        season = Season.objects.first()
        self.assertEquals(str(season), expected_name)

    def test_should_create_one_season(self):
        seasons = Season.objects.all()
        self.assertEquals(seasons.count(), 1)

    def test_should_set_start_date_3_weeks_ago(self):
        today = timezone.now()
        season = Season.objects.first()
        expected_date = today - timedelta(weeks=3)
        self.assertEquals(season.start_date, expected_date.date())

    def test_should_return_four_when_user_ask_about_currently_matchweek(self):
        season = Season.objects.first()
        self.assertEquals(season.matchweek, 4)

    def test_get_currently_season_should_return_currently_season(self):
        season = Season.objects.first()
        self.assertEquals(Season.get_currently_season("Premier League"), season)

    def test_get_currently_season_should_return_none_when_season_does_not_exists(self):
        self.assertFalse(Season.get_currently_season("Does_Not_Exists_League"))

    def test_amt_matchweeks_should_return_six(self):
        season = Season.objects.first()
        self.assertEquals(season.amt_matchweeks, 6)


@tag("team")
class TeamTest(SimpleDB):
    @parameterized.expand([1, 2, 3, 4])
    def test_get_absolute_url(self, pk):
        expected = reverse("league:team-detail", kwargs={"pk": pk})
        team = Team.objects.get(pk=pk)
        self.assertEquals(team.get_absolute_url(), expected)

    @parameterized.expand([(1, "team_0"), (2, "team_1"), (3, "team_2"), (4, "team_3")])
    def test_team_name(self, pk, expected):
        team = Team.objects.get(pk=pk)
        self.assertEquals(str(team), expected)

    def test_should_create_four_teams(self):
        self.assertEquals(Team.objects.count(), 4)

    @parameterized.expand([(1, "team_0"), (2, "team_1"), (3, "team_2"), (4, "team_3")])
    def test_should_create_appropriate_name_team(self, pk, name):
        self.assertEquals(Team.objects.get(pk=pk).name, name)


@tag("teamstats")
class TeamStatsTest(SimpleDB):
    @parameterized.expand([(1, "team_0"), (2, "team_1"), (3, "team_2"), (4, "team_3")])
    def test_teamstate_name(self, pk, team_name):
        ts = TeamStats.objects.get(pk=pk)
        season_date = str(ts.season.start_date.year)
        expected = f"{team_name} {season_date[2:]} {ts.points}"
        self.assertEquals(str(ts), expected)

    @parameterized.expand([1, 2, 3, 4])
    def test_goal_different(self, pk):
        ts = TeamStats.objects.get(pk=pk)
        diff = ts.goals_for - ts.goals_against
        self.assertEquals(diff, ts.goal_difference)

    @parameterized.expand([(1, 4), (2, 3), (3, 1), (4, 2)])
    def test_get_position(self, pk, expected):
        ts = TeamStats.objects.get(pk=pk)
        self.assertEquals(ts.get_position, expected)

    def test_get_season_table_should_first_place_team_2_and_last_place_team_0(self):
        year = (timezone.now() - timedelta(weeks=3)).year
        table = TeamStats.get_season_table("Premier League", year)

        self.assertEquals(table.first().team.name, "team_2")
        self.assertEquals(table.last().team.name, "team_0")

    @parameterized.expand([1, 2, 3, 4])
    def test_get_season_so_far_should_return_appropriated_stats(self, pk):
        ts = TeamStats.objects.get(pk=pk)
        season = Season.objects.first()
        avg_goals_scored_expected = ts.goals_for / ts.played
        avg_goals_conceded_expected = ts.goals_against / ts.played

        season_so_far = TeamStats.get_season_so_far(season, ts.team)

        self.assertEquals(season_so_far.avg_goals_scored, avg_goals_scored_expected)
        self.assertEquals(season_so_far.avg_goals_conceded, avg_goals_conceded_expected)

    def test_get_team_stats_should_sum_extra_when_add_old_season(self):
        team = Team.objects.first()
        league = League.objects.first()
        today = timezone.now()
        season = SeasonFactory(
            start_date=today - timedelta(days=365),
            end_date=today - timedelta(days=300),
            league=league,
            is_currently=False,
        )

        # New team stats 2 won, 2 draw, 2 lost, 6 played, 5 goal_for, 4 goals_against
        won, draw, lost = 2, 2, 2
        played = 6
        goal_for = 5
        goals_against = 4
        points = 8

        TeamStatsFactory(
            team=team,
            season=season,
            played=played,
            won=won,
            drawn=draw,
            lost=lost,
            goals_for=goal_for,
            goals_against=goals_against,
            points=points,
        )

        ts = TeamStats.get_team_stats(team)

        self.assertEquals(ts["played"], 9)
        self.assertEquals(ts["wins"], 2)
        self.assertEquals(ts["losses"], 5)

    @parameterized.expand([(1, 0, 3), (1, 1, 1), (0, 1, 0)])
    def test_update_stats(self, team_goal, opponent_goal, extra_points):
        ts = TeamStats.objects.first()
        points = ts.__dict__["points"]
        ts.update_stats(team_goal, opponent_goal)

        self.assertEquals(ts.points, points + extra_points)
