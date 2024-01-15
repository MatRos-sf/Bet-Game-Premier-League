import json
import os
from datetime import datetime
from http import HTTPStatus

import mock
from django.conf import settings
from django.test import TestCase, tag
from football_data.premier_league import (
    League,
    Match,
    Matchweek,
    PremierLeague,
    Season,
    Team,
    TeamStats,
)
from parameterized import parameterized


@tag("PremierLeague")
class PremierLeagueTest(TestCase):
    def setUp(self):
        self.base_url = "http://api.football-data.org/v4/"
        self.sample_league = League("Test_name", "Test_country", "Test_emblem")

    def __load_payload(self, name_file: str) -> dict:
        file_path = os.path.join(
            settings.BASE_DIR, "football_data", "tests", "payload", name_file
        )
        with open(file_path) as file:
            payload = json.load(file)
        return payload

    def test_url(self):
        self.assertEquals(PremierLeague.API, self.base_url)

    def test_headers_should_has_key(self):
        pl = PremierLeague()
        self.assertIsInstance(pl.headers["X-Auth-Token"], str)

    @parameterized.expand(
        [
            ("new", []),
            ("ssss", []),
            ("url", ["new"]),
            ("test", ["test", "test", "test"]),
        ]
    )
    def test_should_create_url_without_filter(self, url, filters):
        pl = PremierLeague()
        get_full_url = pl._PremierLeague__get_full_url(url, filters).split(
            self.base_url
        )[-1]
        expected = url
        if filters:
            expected += "?" + "&".join(filters)

        self.assertEquals(get_full_url, expected)

    def test_should_raise_error_when_user_do_not_provide_url(self):
        with self.assertRaises(TypeError):
            pl = PremierLeague()
            pl._PremierLeague__get_full_url()

    def test_get_league_should_create_league_object(self):
        pl = PremierLeague()
        expected = League(
            "Premier League", "England", "https://crests.football-data.org/PL.png"
        )
        payload = self.__load_payload("payload.json")

        self.assertEquals(pl.get_league(payload), expected)

    @parameterized.expand(
        [
            ({"name": "Test"},),
            ({"area": {"name": "test"}},),
            ({"emblem": "testemblem"},),
        ]
    )
    def test_get_league_should_not_create_object_when_some_key_does_not_exists(
        self, payload
    ):
        with self.assertRaises(KeyError):
            pl = PremierLeague()
            pl.get_league(payload)

    def test_get_season_should_create_season_when_payload_is_correctly(self):
        pl = PremierLeague()
        pl.league = self.sample_league
        expected = Season(
            fb_id=1564,
            start_date=datetime.strptime("2023-08-11", "%Y-%m-%d"),
            end_date=datetime.strptime("2024-05-19", "%Y-%m-%d"),
            matchweek=13,
            is_currently=True,
            league=pl.league,
        )
        payload = self.__load_payload("payload.json")
        actually = pl.get_season(payload)
        self.assertEquals(actually, expected)

    def test_get_season_should_raise_valueerror_when_league_is_not_set(self):
        pl = PremierLeague()
        payload = self.__load_payload("payload.json")
        with self.assertRaises(ValueError):
            pl.get_season(payload)

    @parameterized.expand(
        [
            ({"samle": 1},),
            ({"currentSeason": {"id": 123}},),
            ({"currentSeason": {"startDate": "2021-01-03"}},),
        ]
    )
    def test_get_season_should_raise_keyerror_when_payload_do_not_some_key(
        self, payload: dict
    ):
        pl = PremierLeague()
        pl.league = self.sample_league
        with self.assertRaises(KeyError):
            pl.get_season(payload)

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_teams_should_return_twenty_teams(self, get_response: mock.MagicMock):
        payload = self.__load_payload("payload_teams.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        pl = PremierLeague()
        teams = pl.get_teams()
        self.assertEquals(len(teams), 20)
        self.assertIsInstance(teams[0], Team)

    @parameterized.expand(
        [
            ({"no_teams": None},),
            ({"teams": [{"name": "test_team"}]},),
            ({"teams": None},),
        ]
    )
    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_teams_should_raise_keyerror_when_some_key_does_not_exist(
        self, payload: dict, get_response: mock.MagicMock
    ):
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        pl = PremierLeague()

        with self.assertRaises(KeyError):
            pl.get_teams()

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_matches_should_return_380_matches(self, get_response: mock.MagicMock):
        payload = self.__load_payload("payload_matches.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        expected_matches = 380
        expected_start_date = datetime.strptime("2023-08-11", "%Y-%m-%d").date()
        expected_end_date = datetime.strptime("2024-05-19", "%Y-%m-%d").date()

        pl = PremierLeague()
        matches = pl.get_matches(2023)
        self.assertEquals(len(matches), expected_matches)

        self.assertEquals(matches[0].start_date.date(), expected_start_date)
        self.assertEquals(matches[-1].start_date.date(), expected_end_date)

    @tag("test_x")
    def test_capture_match_when_data_is_correctly(self):
        payload = self.__load_payload("payload_matches.json")
        pl = PremierLeague()
        matche = pl.capture_match(payload["matches"][0])
        self.assertIsInstance(matche, Match)

    def test_capture_match_when_data_is_empty(self):
        pl = PremierLeague()
        with self.assertRaises(KeyError):
            pl.capture_match({})

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_matchweeks_should_return_38_matchweeks(
        self, get_response: mock.MagicMock
    ):
        payload = self.__load_payload("payload_matches.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        pl = PremierLeague()
        pl.teams = range(20)
        matches = pl.get_matches(2023)
        matchweeks = pl.get_matchweeks(matches)

        self.assertEquals(len(matchweeks), 38)

    def test_get_matchweeks_should_raise_indexerror_list_when_matches_is_empty(self):
        pl = PremierLeague()
        pl.teams = range(20)
        matches = []
        with self.assertRaises(IndexError):
            pl.get_matchweeks(matches)

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_standings_should_return_list_of_teams_stats(
        self, get_response: mock.MagicMock
    ):
        payload = self.__load_payload("payload_standings.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        pl = PremierLeague()
        stats = pl.get_standings()

        self.assertEquals(len(stats), 20)
        self.assertTrue(all(isinstance(team_stats, TeamStats) for team_stats in stats))

    @parameterized.expand(
        [
            ({"no_teams": None},),
            ({"teams": [{"name": "test_team"}]},),
            ({"teams": None},),
        ]
    )
    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_get_standings_should_raise_keyerror_when_provide_data_do_not_heave_key(
        self, payload: dict, get_response: mock.MagicMock
    ):
        response = mock.MagicMock()
        response.json.return_value = payload
        get_response.return_value = (True, response)

        pl = PremierLeague()

        with self.assertRaises(KeyError):
            pl.get_standings()

    def test_pull_should_set_all_attribute(self):
        """
        WARING! Test run correctly if api response.status == OK
        """
        pl = PremierLeague()
        pl.pull()

        self.assertTrue(isinstance(pl.league, League))
        self.assertTrue(isinstance(pl.season, Season))
        self.assertTrue(
            all(isinstance(matchweek, Matchweek) for matchweek in pl.matchweek)
        )
        self.assertTrue(all(isinstance(team, Team) for team in pl.teams))
        self.assertTrue(
            all(isinstance(team_stats, TeamStats) for team_stats in pl.standings)
        )

    def test_convert_season_to_dict_should_convert_when_season_exists(self):
        season = Season(
            1, datetime(2023, 11, 27), datetime(2024, 11, 27), mock.MagicMock, 2, True
        )

        pl = PremierLeague()
        pl.season = season
        season_dict = pl.convert_season_to_dict()

        self.assertIsInstance(season_dict, dict)

    def test_convert_season_to_dict_should_not_convert_when_season_does_not_exists(
        self,
    ):
        pl = PremierLeague()
        with self.assertRaises(AttributeError):
            pl.convert_season_to_dict()

    def test_convert_league_to_dict_should_convert_when_league_exists(self):
        pl = PremierLeague()
        pl.league = self.sample_league
        season_dict = pl.convert_league_to_dict()

        self.assertIsInstance(season_dict, dict)

    def test_convert_league_to_dict_should_not_convert_when_league_does_not_exists(
        self,
    ):
        pl = PremierLeague()
        with self.assertRaises(AttributeError):
            pl.convert_season_to_dict()

    def test_check_new_season_should_return_true(self):
        pl = PremierLeague()
        self.assertTrue(pl.check_new_season(2022))

    @parameterized.expand(
        [
            (
                {"currentSeason": {"startDate": "2023-02-02"}},
                2023,
            ),
            (
                {"currentSeason": {"startDate": "1995-02-02"}},
                1995,
            ),
            (
                {"currentSeason": {"startDate": "2000-02-02"}},
                2000,
            ),
        ]
    )
    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_check_new_season_should_return_true_when_season_is_currently(
        self, payload: dict, season: int, api_response: mock.MagicMock
    ):
        response = mock.MagicMock()
        response.json.return_value = payload
        response.status_code.return_value = HTTPStatus.OK
        api_response.return_value = (True, response)

        pl = PremierLeague()
        self.assertFalse(pl.check_new_season(season))

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_check_match_should_return_none_if_match_is_canceled(self, mock_payload):
        payload = self.__load_payload("payload_check_match.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        mock_payload.return_value = (True, response)

        pl = PremierLeague()
        actually = pl.check_match(2023, 17, 1044, 389)
        self.assertIsNone(actually)

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_check_match_should_return_score_when_match_is_finished(self, mock_payload):
        payload = self.__load_payload("payload_check_match.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        mock_payload.return_value = (True, response)

        expected = {"home": 2, "away": 0}
        pl = PremierLeague()
        actually = pl.check_match(2023, 17, 61, 356)

        self.assertDictEqual(expected, actually)

    @mock.patch(
        "football_data.premier_league.PremierLeague._PremierLeague__get_response"
    )
    def test_check_match_should_return_none_when_ids_do_not_contains_in_payload(
        self, mock_payload
    ):
        payload = self.__load_payload("payload_check_match.json")
        response = mock.MagicMock()
        response.json.return_value = payload
        mock_payload.return_value = (True, response)

        pl = PremierLeague()
        actually = pl.check_match(2023, 17, 33333, 2222)

        self.assertIsNone(actually)
