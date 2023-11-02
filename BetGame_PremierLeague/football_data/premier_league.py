import os
from dataclasses import dataclass
import requests
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from datetime import datetime
from django.utils import timezone
from time import sleep

load_dotenv()

HEADER = {"X-Auth-Token": str(os.getenv("API_TOKEN"))}
# TODO basic Legue gdzie będzie dziedziczone dzięki tej klasie będzie można stworzyć różne ligi


# https://reqbin.com/code/python/3zdpeao1/python-requests-timeout-example


@dataclass
class League:
    name: str
    country: str
    emblem: str


@dataclass
class Season:
    fb_id: int
    start_date: datetime.date
    end_date: datetime.date
    league: League
    matchweek: int
    is_currently: bool


@dataclass
class Team:
    fb_id: int
    name: str
    short_name: str
    shortcut: str
    currently_league: League | None
    crest: str
    website: str
    club_colours: str

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return f"{self.name}"


@dataclass
class Match:
    home_team_id: int
    away_team_id: int
    start_date: datetime.date
    home_goals: int
    away_goals: int
    finished: bool
    matchweek: int


@dataclass
class Matchweek:
    matchweek: int
    start_date: datetime.date
    end_date: datetime.date
    season: Season
    finished: bool
    matches: List[Match]


class PremierLeague:
    API = "http://api.football-data.org/v4/"

    def __init__(self):
        self.league: League | None = None
        self.season: Season | None = None
        self.teams: List[Team] = []
        self.matchweek: List[Matchweek] = []

        self.shortcut_league = "PL"
        self.name_league = "Premier League"
        self.url_competitions: str = "competitions/PL/teams"
        self.url_current_season: str = "competitions/PL"
        self.url_standings: str = "competitions/PL/standings"
        self.url_matchweek: str = "competitions/PL/matches"
        self.headers: Dict[str, str] = HEADER

    def __get_full_url(self, url: str, filter=None):
        if filter:
            return PremierLeague.API + url + "?" + "&".join(filter)
        return PremierLeague.API + url

    def __get_response(self, url: str) -> Tuple[bool, requests.Response | None]:
        try:
            response = requests.get(url=url, headers=self.headers, timeout=5)
        except requests.exceptions.Timeout:
            return False, None

        return True, response

    def pull(self):
        url = self.__get_full_url(self.url_current_season)
        succeed, response = self.__get_response(url)

        if not succeed or response.status_code != 200:
            return

        dataset = response.json()

        # connect with server
        self.league = self.get_league(dataset)
        self.season = self.get_season(dataset)

        # get teams
        self.teams = self.get_teams()

        # get Matches
        matches = self.get_matches(self.season.start_date.year)
        # sort and create Matchweek
        self.matchweek = self.get_matchweeks(matches)

    def get_league(self, dataset: dict):
        name = dataset["name"]
        country = dataset["area"]["name"]
        emblem = dataset["emblem"]

        return League(name, country, emblem)

    def get_season(self, dataset: dict):
        if not self.league:
            raise ValueError("You don't set League!")

        fb_id = dataset["currentSeason"]["id"]
        start_date = datetime.strptime(
            dataset["currentSeason"]["startDate"], "%Y-%m-%d"
        )
        end_date = datetime.strptime(dataset["currentSeason"]["endDate"], "%Y-%m-%d")
        matchweek = dataset["currentSeason"]["currentMatchday"]
        is_currently = dataset["currentSeason"]["winner"] == None

        return Season(
            fb_id=fb_id,
            start_date=start_date,
            end_date=end_date,
            matchweek=matchweek,
            is_currently=is_currently,
            league=self.league,
        )

    def get_teams(self, league: League = None):
        """
        The method retrieves information about teams. It returns a list of Team objects.
        """
        url = self.__get_full_url(self.url_competitions)
        succeed, response = self.__get_response(url)

        if not succeed:
            return
        dataset = response.json()["teams"]

        teams: List[Team] = []

        for team in dataset:
            team_obj = Team(
                fb_id=team["id"],
                name=team["name"],
                short_name=team["shortName"],
                shortcut=team["tla"],
                crest=team["crest"],
                website=team["website"],
                club_colours=team["clubColors"],
                currently_league=league,
            )

            teams.append(team_obj)

        return teams

    def get_matches(self, year: int, finished: bool = True) -> List[Match] | None:
        """
        The method retrieves information about all season matches.
        It returns a list of Match objects.
        """
        url = self.__get_full_url(self.url_matchweek, [f"&season={str(year)}"])
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        dataset = response.json()

        matches = list()

        for match in dataset["matches"]:
            match_obj = Match(
                home_team_id=match["homeTeam"]["id"],
                away_team_id=match["awayTeam"]["id"],
                start_date=datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ"),
                home_goals=match["score"]["fullTime"]["home"],
                away_goals=match["score"]["fullTime"]["away"],
                finished=match["status"] == "FINISHED",
                matchweek=match["matchday"],
            )

            matches.append(match_obj)

        return matches

    def get_matchweeks(self, matches: List[Match]) -> List[Matchweek]:
        from operator import attrgetter

        all_matchweek = (len(self.teams) * 2) - 1
        matchweeks = list()
        matches = sorted(matches, key=attrgetter("matchweek", "start_date"))

        for mw in range(1, all_matchweek):
            mw_matches = [match for match in matches if match.matchweek == mw]
            start_date = mw_matches[0].start_date
            end_date = mw_matches[-1].start_date
            matchweek_obj = Matchweek(
                matchweek=mw,
                start_date=start_date,
                end_date=end_date,
                season=self.season,
                finished=end_date > datetime.now(),
                matches=mw_matches,
            )

        return matchweek_obj

    # below probably delete
    def get_info_currently_league(self) -> Dict[str, str] | None:
        url = self.__get_full_url(self.url_competitions)
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        response_league_ino = response.json()["competition"]
        league = {
            "name": response_league_ino["name"],
            "emblem": response_league_ino["emblem"],
            "country": "England",
        }

        return league

    def get_info_current_season(self) -> Dict[str, str] | None:
        url = self.__get_full_url(self.url_current_season)
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        data = response.json()

        season = {
            "league": data["name"],
            "fb_id": data["currentSeason"]["id"],
            "start_date": data["currentSeason"]["startDate"],
            "end_date": data["currentSeason"]["endDate"],
            "matchweek": data["currentSeason"]["currentMatchday"],
        }

        return season

    def get_current_standings(
        self,
    ) -> Tuple[str, List[Dict[str, str]]] | Tuple[None, None]:
        url = self.__get_full_url(self.url_standings)
        succeed, response = self.__get_response(url)

        if not succeed:
            return None, None

        data = response.json()

        season_id: str = data["season"]["id"]

        table = data["standings"][0]["table"]

        pl_table = []

        for position in table:
            payload = {}

            payload["fb_id"] = position["team"]["id"]
            payload["played"] = position["playedGames"]
            payload["won"] = position["won"]
            payload["drawn"] = position["draw"]
            payload["lost"] = position["lost"]
            payload["goals_for"] = position["goalsFor"]
            payload["goals_against"] = position["goalsAgainst"]
            payload["points"] = position["points"]

            pl_table.append(payload)

        return season_id, pl_table

    def get_matches_result(
        self, mw: int, year: int
    ) -> Tuple[Dict[str, str], List[Dict[str, str]]] | Tuple[None, None]:
        """
        Return only finished matches
        """
        url = self.__get_full_url(
            self.url_matchweek, [f"matchday={str(mw)}", f"season={str(year)}"]
        )
        succeed, response = self.__get_response(url)

        if not succeed:
            return None, None

        data = response.json()

        info = {
            "all": data["resultSet"]["count"],
            "played": data["resultSet"]["played"],
        }

        matches = []

        for match in data["matches"]:
            payload = {}

            if match["status"] != "FINISHED":
                continue

            payload["home_team_id"] = match["homeTeam"]["id"]
            payload["away_team_id"] = match["awayTeam"]["id"]
            payload["home_goals"] = match["score"]["fullTime"]["home"]
            payload["away_goals"] = match["score"]["fullTime"]["away"]

            matches.append(payload)

        return info, matches
