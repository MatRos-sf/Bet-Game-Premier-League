from league.tests.test_models import SimpleDB
from parameterized import parameterized
from django.test import tag
from django.core.exceptions import ValidationError
from django.urls import reverse

from league.models import League, Team, Season
from match.models import Matchweek, Match


@tag("matchweek")
class MatchweekTest(SimpleDB):
    @parameterized.expand([1, 2, 3, 4, 5, 6])
    def test_model_str(self, pk):
        mw = Matchweek.objects.get(matchweek=pk)
        season_date = str(mw.start_date.year)
        expected = f"Matchweek {mw.matchweek}/{season_date[2:]}"
        self.assertEquals(str(mw), expected)

    @parameterized.expand([4, 5, 6])
    def test_should_raise_validation_error_when_user_try_save_finish_matchweek_but_matches_are_not_finished(
        self, pk
    ):
        with self.assertRaises(ValidationError):
            mw = Matchweek.objects.get(matchweek=pk)
            mw.finished = True
            mw.save()

    @parameterized.expand([1, 2, 3, 4, 5, 6])
    def test_matches_count_should_return_two(self, matchweek):
        mw = Matchweek.objects.get(matchweek=matchweek)
        self.assertEquals(mw.matches_count, 2)

    @parameterized.expand([(1, 2), (2, 2), (3, 2), (4, 0), (5, 0), (6, 0)])
    def test_matches_played_should_return_appropriated_expected(
        self, matchweek, expected
    ):
        mw = Matchweek.objects.get(matchweek=matchweek)
        self.assertEquals(mw.matches_played, expected)

    @parameterized.expand(
        [(1, True), (2, True), (3, True), (4, False), (5, False), (6, False)]
    )
    def test_is_finished_should_return_appropriated_expected(self, matchweek, expected):
        mw = Matchweek.objects.get(matchweek=matchweek)
        self.assertEquals(mw.is_finished(), expected)


@tag("match")
class MatchTest(SimpleDB):
    @parameterized.expand([0, 1, 2, 3, 4, 5])
    def test_model_str_when_match_finished(self, index):
        match = Match.objects.all()[index]
        expected = f"{match.pk}: {match.home_team} vs {match.away_team} {match.score}"
        self.assertEquals(str(match), expected)

    @parameterized.expand([6, 7, 8, 9, 10, 11])
    def test_model_str_when_match_finished(self, index):
        match = Match.objects.all()[index]
        expected = f"{match.home_team} vs {match.away_team} "
        self.assertEquals(str(match), expected)

    @parameterized.expand([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    def test_get_absolute_url_match(self, index):
        match = Match.objects.all()[index]
        expected = reverse("match:detail", kwargs={"pk": match.pk})

        self.assertEquals(match.get_absolute_url(), expected)

    @parameterized.expand([(2, ("away", "team_2")), (4, ("home", "team_3"))])
    def test_winner_when_won_home_or_away(self, index, expected):
        match = Match.objects.all()[index]
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1].name, expected[1])

    def test_winner_when_draw(self):
        match = Match.objects.all()[5]
        expected = "draw", True
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1], expected[1])

    def test_winner_when_match_not_finished(self):
        match = Match.objects.all()[6]
        expected = None, None
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1], expected[1])

    @parameterized.expand([0, 2, 4, 6, 8])
    def test_league_should_return_premier_league(self, index):
        match = Match.objects.all()[index]

        self.assertEquals(match.league.name, "Premier League")

    def test_get_last_match_should_return_match_team1_vs_team2_when_user_give_team(
        self,
    ):
        team = Team.objects.get(name="team_1")
        last_match = Match.get_last_match(team)

        self.assertEquals(last_match.home_team.name, "team_1")
        self.assertEquals(last_match.away_team.name, "team_2")

        self.assertTrue(last_match.finished)

    @parameterized.expand([0, 1, 2, 3])
    def test_get_season_finished_matches(self, index):
        season = Season.objects.first()
        team = Team.objects.all()[index]

        finished_matches = Match.get_season_finished_matches(team, season)

        self.assertEquals(finished_matches.count(), 3)

    @parameterized.expand([(0, 0), (1, 1), (2, 1), (3, 1)])
    def test_get_clean_sheets_should_return_appropriate_team_clean_sheet(
        self, index, expected
    ):
        team = Team.objects.all()[index]
        season = Season.objects.first()

        result = Match.get_clean_sheets(team, season)

        self.assertEquals(result, expected)

    def test_get_next_match_should_return_team_0_next_matches(self):
        team = Team.objects.first()
        result = Match.get_next_match(team)

        self.assertEquals(result.home_team.name, "team_0")
        self.assertEquals(result.away_team.name, "team_3")
