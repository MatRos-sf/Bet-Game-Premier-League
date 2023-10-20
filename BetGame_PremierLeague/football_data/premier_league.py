import requests
from typing import Dict, List

HEADER = {
    'X-Auth-Token': 'b77f4c1f9e31408ebe32979cb77c92e4'
}


class PremierLeague:

    API = "http://api.football-data.org/v4/"

    def __init__(self):

        self.competitions: str = 'competitions/PL/teams'
        self.headers: Dict[str, str] = HEADER

    def get_info_currently_league(self) -> Dict[str, str]:

        url = self.API + self.competitions
        response = requests.get(url, headers=HEADER)

        response_league_ino = response.json()['competition']
        league = {
            'name': response_league_ino['name'],
            'emblem': response_league_ino['emblem'],
            'country': 'England'
        }

        return league

    def get_info_currently_teams_in_league(self) -> List[Dict[str, str]] | None:

        url = self.API + self.competitions
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








