import requests
from typing import Dict, List, Tuple
from datetime import datetime
HEADER = {
    'X-Auth-Token': 'b77f4c1f9e31408ebe32979cb77c92e4'
}


class PremierLeague:

    API = "http://api.football-data.org/v4/"

    def __init__(self):

        self.url_competitions: str = 'competitions/PL/teams'
        self.url_current_season: str = 'competitions/PL'
        self.url_standings: str = 'competitions/PL/standings'
        self.url_matchweek: str = 'competitions/PL/matches'
        self.headers: Dict[str, str] = HEADER

    def get_info_currently_league(self) -> Dict[str, str]:

        url = self.API + self.url_competitions
        response = requests.get(url, headers=HEADER)

        response_league_ino = response.json()['competition']
        league = {
            'name': response_league_ino['name'],
            'emblem': response_league_ino['emblem'],
            'country': 'England'
        }

        return league

    def get_info_currently_teams_in_league(self) -> Tuple[str, List[Dict[str, str]] | None]:

        url = self.API + self.url_competitions
        response = requests.get(url, headers=HEADER)

        data = response.json()

        league_name = data['competition']['name']
        response_teams_ino = data['teams']

        teams = []

        for team in response_teams_ino:
            team_payload = {}

            team_payload['id_from_fd'] = team['id']
            team_payload['name'] = team['name']
            team_payload['short_name'] = team['shortName']
            team_payload['shortcut'] = team['tla']
            team_payload['crest'] = team['crest']
            team_payload['website'] = team['website']
            team_payload['club_colours'] = team['clubColors']

            teams.append(team_payload)

        return league_name, teams

    def get_info_current_season(self) -> Dict[str, str]:
        url = self.API + self.url_current_season
        response = requests.get(url, headers=HEADER)

        data = response.json()

        season = {
            'league': data['name'],
            'id_form_fd': data['currentSeason']['id'],
            'start_date': data['currentSeason']['startDate'],
            'end_date': data['currentSeason']['endDate'],
            'matchweek': data['currentSeason']['currentMatchday']
        }

        return season

    def get_current_standings(self) -> Tuple[str, List[Dict[str, str]]]:

        url = self.API + self.url_standings
        response = requests.get(url, headers=HEADER)

        data = response.json()

        season_id: str = data['season']['id']

        table = data['standings'][0]['table']

        pl_table = []

        for position in table:
            payload = {}

            payload['id_from_fd'] = position['team']['id']
            payload['played'] = position['playedGames']
            payload['won'] = position['won']
            payload['drawn'] = position['draw']
            payload['lost'] = position['lost']
            payload['goals_for'] = position['goalsFor']
            payload['goals_against'] = position['goalsAgainst']
            payload['points'] = position['points']

            pl_table.append(payload)

        return season_id, pl_table

    def get_matchweek(self, value, year=None) -> Tuple[Dict[str, str], List[Dict[str,str]]]:

        url = self.API + self.url_matchweek + f"?matchday={str(value)}"
        if year:
            url += f"&season={str(year)}"

        response = requests.get(url, headers=HEADER)

        data = response.json()

        matchweek_data = data
        matches_data = data['matches']

        matchweek = dict()

        matchweek['start_date'] = matchweek_data['resultSet']['first']
        matchweek['end_date'] = matchweek_data['resultSet']['last']


        matches = list()
        for match in matches_data:
            payload = dict()

            payload['home_team_id'] = match['homeTeam']['id']
            payload['away_team_id'] = match['awayTeam']['id']
            payload['start_date'] = match['utcDate']

            matches.append(payload)
        return matchweek, matches

    def get_