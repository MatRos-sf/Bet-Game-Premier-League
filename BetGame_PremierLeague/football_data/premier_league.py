from dataclasses import dataclass
import requests
from requests.exceptions import HTTPError, Timeout
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from datetime import datetime
from django.utils import timezone
from http import HTTPStatus
from django.conf import settings

load_dotenv()

HEADER = {"X-Auth-Token": settings.API_TOKEN}
# HEADER = {"X-Auth-Token": str(os.getenv("API_TOKEN"))}


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
    start_date: datetime
    home_goals: int
    away_goals: int
    finished: bool
    cancelled: bool
    matchweek: int


@dataclass
class Matchweek:
    matchweek: int
    start_date: datetime
    end_date: datetime
    season: Season
    finished: bool
    matches: List[Match]


@dataclass
class TeamStats:
    team_fb_id: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    points: int


class PremierLeague:
    API = "http://api.football-data.org/v4/"

    def __init__(self):
        self.league: Optional[League] = None
        self.season: Optional[Season] = None
        self.teams: List[Team] = []
        self.matchweek: List[Matchweek] = []
        self.standings: List[TeamStats] = []

        self.shortcut_league = "PL"
        self.name_league = "Premier League"
        self.url_competitions: str = "competitions/PL/teams"
        self.url_current_season: str = "competitions/PL"
        self.url_standings: str = "competitions/PL/standings"
        self.url_matchweek: str = "competitions/PL/matches"
        self.headers: Dict[str, str] = HEADER

    def __get_full_url(self, url: str, filters: Optional[List[str]] = None):
        if filters:
            return PremierLeague.API + url + "?" + "&".join(filters)
        return PremierLeague.API + url

    def __get_response(self, url: str) -> Tuple[bool, requests.Response | None]:
        try:
            response = requests.get(url=url, headers=self.headers, timeout=5)
        except Timeout:
            raise Timeout("Can't connect with server!")

        if response.status_code == HTTPStatus.FORBIDDEN:
            raise HTTPError(
                "The resource you are looking for is restricted and apparently not within your permissions. Please check your subscription."
            )
        elif response.status_code != HTTPStatus.OK:
            raise HTTPError("The status code cannot be different than 200.")

        return True, response

    def pull(self) -> None:
        url = self.__get_full_url(self.url_current_season)
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        dataset = response.json()

        # set league, season
        self.league = self.get_league(dataset)
        self.season = self.get_season(dataset)

        # set teams
        self.teams = self.get_teams()

        # set matches and matchweeks
        matches = self.get_matches(self.season.start_date.year)
        # sort and create Matchweek
        self.matchweek = self.get_matchweeks(matches)

        # set current standing
        self.standings = self.get_standings()

    def update_score_matches(self, mw: int) -> List[Match]:
        """
        Retrieve information on current football matches from football-data. Return provide
        scores feedback and verify if the matchweek is ended.
        """
        url = self.__get_full_url(self.url_matchweek, [f"matchday={str(mw)}"])
        _, response = self.__get_response(url)

        dataset = response.json()

        matches = []

        for match in dataset["matches"]:
            m = self.capture_match(match)
            matches.append(m)

        return matches

    @staticmethod
    def get_league(dataset: dict) -> League:
        name: str = dataset["name"]
        country: str = dataset["area"]["name"]
        emblem: str = dataset["emblem"]

        return League(name, country, emblem)

    def get_season(self, dataset: dict) -> Season:
        if not self.league:
            raise ValueError("You don't set League!")

        fb_id: int = dataset["currentSeason"]["id"]
        start_date: datetime = datetime.strptime(
            dataset["currentSeason"]["startDate"], "%Y-%m-%d"
        )
        end_date: datetime = datetime.strptime(
            dataset["currentSeason"]["endDate"], "%Y-%m-%d"
        )
        matchweek: int = dataset["currentSeason"]["currentMatchday"]
        is_currently: bool = dataset["currentSeason"]["winner"] is None

        return Season(
            fb_id=fb_id,
            start_date=start_date,
            end_date=end_date,
            matchweek=matchweek,
            is_currently=is_currently,
            league=self.league,
        )

    def get_teams(self, filters: Optional[list] = None) -> Optional[List[Team]]:
        """
        The method retrieves information about teams. It returns a list of Team objects.
        """
        url = self.__get_full_url(self.url_competitions, filters)
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        dataset = response.json()["teams"]

        if not dataset:
            raise KeyError("Empty list of Teams!")

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
            )

            teams.append(team_obj)

        return teams

    def get_matches(self, year: int) -> Optional[List[Match]]:
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
            match_obj = self.capture_match(match)

            matches.append(match_obj)

        return matches

    def get_matchweeks(self, matches: List[Match]) -> List[Matchweek]:
        """
        The method splits a list of matches by Matchweek and returns a list of Matchweeks.
        """
        from operator import attrgetter

        all_matchweek = (len(self.teams) * 2) - 1
        matchweeks = list()
        matches = sorted(matches, key=attrgetter("matchweek", "start_date"))

        for mw in range(1, all_matchweek):
            mw_matches = [match for match in matches if match.matchweek == mw]
            start_date = mw_matches[0].start_date.replace(tzinfo=timezone.utc)
            end_date = mw_matches[-1].start_date.replace(tzinfo=timezone.utc)

            matchweek_obj = Matchweek(
                matchweek=mw,
                start_date=start_date,
                end_date=end_date,
                season=self.season,
                finished=end_date < timezone.now(),
                matches=mw_matches,
            )
            matchweeks.append(matchweek_obj)
        return matchweeks

    def get_standings(self) -> List[TeamStats] | None:
        """
        The method that retrieves information about league ranking
        """

        url = self.__get_full_url(self.url_standings)
        succeed, response = self.__get_response(url)

        if not succeed and response.status_code != 200:
            return

        dataset = response.json()["standings"][0]["table"]

        teams_standings = []

        for position in dataset:
            team = TeamStats(
                team_fb_id=position["team"]["id"],
                played=position["playedGames"],
                won=position["won"],
                drawn=position["draw"],
                lost=position["lost"],
                goals_for=position["goalsFor"],
                goals_against=position["goalsAgainst"],
                points=position["points"],
            )

            teams_standings.append(team)

        return teams_standings

    @staticmethod
    def capture_match(data: dict) -> Match:
        date = datetime.strptime(data["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        date = timezone.make_aware(date, timezone=timezone.utc)

        match_obj = Match(
            home_team_id=data["homeTeam"]["id"],
            away_team_id=data["awayTeam"]["id"],
            start_date=date,
            home_goals=data["score"]["fullTime"]["home"],
            away_goals=data["score"]["fullTime"]["away"],
            finished=data["status"] == "FINISHED",
            cancelled=data["status"] == "CANCELLED" or data["status"] == "POSTPONED",
            matchweek=data["matchday"],
        )
        return match_obj

    def convert_season_to_dict(self):
        if not self.season:
            raise AttributeError("The season attribute is None!")
        return self.season.__dict__

    def convert_league_to_dict(self):
        if not self.league:
            raise AttributeError("The league attribute is None!")
        return self.league.__dict__

    def check_new_season(self, season: int) -> Optional[bool]:
        url = self.__get_full_url(self.url_current_season)
        succeed, response = self.__get_response(url)

        if not succeed or response.status_code != HTTPStatus.OK:
            return

        dataset = response.json()
        start_new_season = datetime.strptime(
            dataset["currentSeason"]["startDate"], "%Y-%m-%d"
        )
        return start_new_season.year != season

    def capture_season(self, dataset: dict):
        fb_id: int = dataset["id"]
        start_date: datetime = datetime.strptime(dataset["startDate"], "%Y-%m-%d")
        end_date: datetime = datetime.strptime(dataset["endDate"], "%Y-%m-%d")
        matchweek: int = dataset["currentMatchday"]
        is_currently: bool = False if dataset["winner"] else True

        return Season(
            fb_id=fb_id,
            start_date=start_date,
            end_date=end_date,
            matchweek=matchweek,
            is_currently=is_currently,
            league=self.league,
        )

    def capture_standings(self, dataset: dict) -> List[TeamStats]:
        teams_standings = []

        for position in dataset:
            team = TeamStats(
                team_fb_id=position["team"]["id"],
                played=position["playedGames"],
                won=position["won"],
                drawn=position["draw"],
                lost=position["lost"],
                goals_for=position["goalsFor"],
                goals_against=position["goalsAgainst"],
                points=position["points"],
            )

            teams_standings.append(team)

        return teams_standings

    def capture_previous_season(self, league, currently_season):
        self.league = League(*league)
        season = currently_season - 1

        while season:
            url = self.__get_full_url(self.url_standings, [f"season={season}"])

            try:
                succeed, response = self.__get_response(url)

            except HTTPError:
                break

            dataset = response.json()

            self.season = self.capture_season(dataset["season"])

            self.teams = self.get_teams([f"season={self.season.start_date.year}"])

            matches = self.get_matches(self.season.start_date.year)
            self.matchweek = self.get_matchweeks(matches)

            # set current standing
            self.standings = self.capture_standings(dataset["standings"][0]["table"])

            yield {
                "season": self.season,
                "teams": self.teams,
                "matchweek": self.matchweek,
                "standings": self.standings,
            }

            season -= 1

    def check_match(
        self, season: int, matchweek: int, home_team_id: int, away_team_id: int
    ) -> Optional[Dict[str, int]]:
        """
        Checks match. If match is finished return dict with score otherwise return None
        """
        url = self.__get_full_url(
            self.url_matchweek, [f"season={str(season)}", f"matchday={matchweek}"]
        )
        succeed, response = self.__get_response(url)

        if not succeed:
            return

        dataset = response.json()
        matches = dataset["matches"]

        for match in matches:
            if (
                match["homeTeam"]["id"] == home_team_id
                and match["awayTeam"]["id"] == away_team_id
            ):
                if match["status"] == "FINISHED":
                    return {
                        "home": match["score"]["fullTime"]["home"],
                        "away": match["score"]["fullTime"]["away"],
                    }
                else:
                    return

        return
