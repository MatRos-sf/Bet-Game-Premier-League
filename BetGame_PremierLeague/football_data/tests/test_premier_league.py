from django.test import TestCase, tag
from parameterized import parameterized
import json
import os
from football_data.premier_league import PremierLeague, League, Season, Team, Match
import mock
from datetime import datetime

path_file = os.path.join(os.getcwd(), "football_data", "tests", "payload.json")
file = open(path_file)
PAYLOAD = json.load(file)


@tag("PremierLeague")
class PremierLeagueTest(TestCase):
    def setUp(self):
        self.base_url = "http://api.football-data.org/v4/"
        self.sample_league = League("Test_name", "Test_country", "Test_emblem")

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

    # @mock.patch('football_data.premier_league.PremierLeague._PremierLeague__get_response')
    # def test_s(self, get_response: mock.MagicMock):
    #     response = mock.MagicMock()
    #     response.json.return_value = PAYLOAD
    #     response.json.teams.return_value = PAYLOAD['teams']
    #     get_response.return_value = (True, response)
    #
    #     pl = PremierLeague()
    #     pl.pull()
    #     print(pl.league)

    # https://stackoverflow.com/questions/55512708/how-to-properly-mock-private-members-of-a-class

    def test_get_league_should_create_league_object(self):
        pl = PremierLeague()
        expected = League(
            "Premier League", "England", "https://crests.football-data.org/PL.png"
        )

        self.assertEquals(pl.get_league(PAYLOAD), expected)

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

        actually = pl.get_season(PAYLOAD)
        self.assertEquals(actually, expected)

    def test_get_season_should_raise_valueerror_when_league_is_not_set(self):
        pl = PremierLeague()
        with self.assertRaises(ValueError):
            pl.get_season(PAYLOAD)

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
        file_path = os.path.join(
            os.getcwd(), "football_data", "tests", "payload_teams.json"
        )
        file = open(file_path)
        payload = json.load(file)
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
        file_path = os.path.join(
            os.getcwd(), "football_data", "tests", "payload_matches.json"
        )
        file = open(file_path)
        payload = json.load(file)
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

    def __load_payload(self, name_file: str) -> dict:
        file_path = os.path.join(os.getcwd(), "football_data", "tests", name_file)
        with open(file_path) as file:
            payload = json.load(file)
        return payload

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
