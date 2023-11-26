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
    @parameterized.expand([1, 2, 3, 4, 5, 6])
    def test_model_str_when_match_finished(self, pk):
        match = Match.objects.get(pk=pk)
        expected = f"{pk}: {match.home_team} vs {match.away_team} {match.score}"
        self.assertEquals(str(match), expected)

    @parameterized.expand([7, 8, 9, 10, 11, 12])
    def test_model_str_when_match_finished(self, pk):
        match = Match.objects.get(pk=pk)
        expected = f"{pk}: {match.home_team} vs {match.away_team} "
        self.assertEquals(str(match), expected)

    @parameterized.expand([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    def test_get_absolute_url_match(self, pk):
        expected = reverse("match:detail", kwargs={"pk": pk})
        match = Match.objects.get(pk=pk)

        self.assertEquals(match.get_absolute_url(), expected)

    @parameterized.expand([(1, "0:3"), (2, "5:1"), (7, None), (8, None)])
    def test_score(self, pk, expected):
        match = Match.objects.get(pk=pk)
        self.assertEquals(match.score, expected)

    @parameterized.expand([(3, ("away", "team_2")), (5, ("home", "team_3"))])
    def test_winner_when_won_home_or_away(self, pk, expected):
        match = Match.objects.get(pk=pk)
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1].name, expected[1])

    @parameterized.expand([(6, ("draw", True))])
    def test_winner_when_draw(self, pk, expected):
        match = Match.objects.get(pk=pk)
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1], expected[1])

    @parameterized.expand([(7, (None, None))])
    def test_winner_when_match_not_finished(self, pk, expected):
        match = Match.objects.get(pk=pk)
        winner = match.winner
        self.assertEquals(winner[0], expected[0])
        self.assertEquals(winner[1], expected[1])

    @parameterized.expand([1, 3, 5, 7, 9])
    def test_league_should_return_premier_league(self, pk):
        match = Match.objects.get(pk=pk)

        self.assertEquals(match.league.name, "Premier League")

    def test_get_last_match_should_return_match_team1_vs_team2_when_user_give_team(
        self,
    ):
        team = Team.objects.get(name="team_1")
        last_match = Match.get_last_match(team)

        self.assertEquals(last_match.home_team.name, "team_1")
        self.assertEquals(last_match.away_team.name, "team_2")

        self.assertTrue(last_match.finished)

    def test_get_last_match_should_return_match_team3_vs_team0_when_user_do_not_provide_team(
        self,
    ):
        last_match = Match.get_last_match()

        self.assertEquals(last_match.home_team.name, "team_3")
        self.assertEquals(last_match.away_team.name, "team_0")

        self.assertTrue(last_match.finished)

    @parameterized.expand([1, 2, 3, 4])
    def test_get_season_finished_matches(self, pk):
        season = Season.objects.first()
        team = Team.objects.get(pk=pk)

        finished_matches = Match.get_season_finished_matches(team, season)

        self.assertEquals(finished_matches.count(), 3)

    @parameterized.expand([(1, 0), (2, 1), (3, 1), (4, 1)])
    def test_get_clean_sheets_should_return_appropriate_team_clean_sheet(
        self, pk, expected
    ):
        team = Team.objects.get(pk=pk)
        season = Season.objects.first()

        result = Match.get_clean_sheets(team, season)

        self.assertEquals(result, expected)

    def test_get_next_match_should_return_team_0_next_matches(self):
        team = Team.objects.get(pk=1)
        result = Match.get_next_match(team)

        self.assertEquals(result.home_team.name, "team_0")
        self.assertEquals(result.away_team.name, "team_3")

    def test_get_next_match_should_return_team_0_vs_team_3_next_matches_when_user_does_not_provide_team(
        self,
    ):
        result = Match.get_next_match()
        self.assertEquals(result.home_team.name, "team_0")
        self.assertEquals(result.away_team.name, "team_3")

    # def test_get_form_guide_team_should_return_additional_field(self):
    #
    #     team = Team.objects.get(pk=2)
    #
    #     team_form = Match.get_form_guide_team(team, 3)
    #     for i in team_form:
    #         print(i.result)
    #     # self.assertEquals(team_form[0].w, 'A')
    #     # self.assertEquals(team_form[1].w, 'H')
    #     # self.assertEquals(team_form[2].w, 'A')
    #
    #     self.assertEquals(team_form[0].result, 'W')
    #     self.assertEquals(team_form[1].result, 'L')
    #     self.assertEquals(team_form[2].result, 'D')
