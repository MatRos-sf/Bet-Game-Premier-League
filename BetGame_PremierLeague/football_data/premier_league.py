import requests
from typing import Dict, List, Tuple
from datetime import datetime
HEADER = {
    'X-Auth-Token': 'b77f4c1f9e31408ebe32979cb77c92e4'
}


# def convert_date(date: str) -> str:
#     """
#     The function convert date %y-%m-%d to %d/%m/%y
#     """
#     date = datetime.strptime(date, "%Y-%m-%d")
#
#     return date.strftime('%d/%m/%Y')
#

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

    def get_info_currently_teams_in_league(self) -> List[Dict[str, str]] | None:

        url = self.API + self.url_competitions
        response = requests.get(url, headers=HEADER)

        response_teams_ino = response.json()['teams']

        teams = []

        for team in response_teams_ino:
            team_payload = {}

            team_payload['name'] = team['name']
            team_payload['short_name'] = team['shortName']
            team_payload['shortcut'] = team['tla']
            team_payload['crest'] = team['crest']
            team_payload['website'] = team['website']
            team_payload['club_colours'] = team['clubColors']

            teams.append(team_payload)

        return teams

    def get_info_current_season(self) -> Dict[str, str]:
        url = self.API + self.url_current_season
        response = requests.get(url, headers=HEADER)

        current = response.json()['currentSeason']
        season = {
            'start_date': current['startDate'],
            'end_date': current['endDate'],
            'matchweek': current['currentMatchday']
        }

        return season

    def get_current_standings(self) -> Tuple[Dict[str, str], List[Dict[str, str]]]:

        url = self.API + self.url_standings
        response = requests.get(url, headers=HEADER)

        season = response.json()['season']
        season_info = {
            'start_date': season['startDate'],
            'end_date': season['endDate']
        }

        table = response.json()['standings'][0]['table']

        pl_table = []

        for position in table:
            payload = {}

            payload['team'] = position['team']['name']
            payload['played'] = position['playedGames']
            payload['won'] = position['won']
            payload['drawn'] = position['draw']
            payload['lost'] = position['lost']
            payload['goals_for'] = position['goalsFor']
            payload['goals_against'] = position['goalsAgainst']
            payload['points'] = position['points']

            pl_table.append(payload)

        return season_info, pl_table

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

            payload['home_team'] = match['homeTeam']['name']
            payload['awayTeam'] = match['awayTeam']['name']
            payload['start_date'] = match['utcDate']

            matches.append(payload)
        return matchweek, matches

