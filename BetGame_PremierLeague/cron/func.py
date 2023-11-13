from requests.exceptions import HTTPError, Timeout

from match.models import Matchweek, Match
from football_data.premier_league import PremierLeague
from league.models import League, Team, Season, TeamStats


# TODO change name: check_and_update_currently_matchweek
def check_and_update_currently_matchweek() -> str:
    """
    Checks the current matchweek stored in the database and compares it with the data from football-data.api.
    If there are discrepancies, updates the matches and matchweek accordingly.
    :return:
    """
    matchweek = Matchweek.objects.filter(finished=False).first()

    pl = PremierLeague()
    try:
        finished_matches = pl.update_score_matches(matchweek.matchweek)
    except (HTTPError, Timeout) as e:
        return f"Something wrong: \n{e}"

    for match in finished_matches:
        match_obj = Match.objects.get(
            matchweek=matchweek,
            home_team__fb_id=match.home_team_id,
            away_team__fb_id=match.away_team_id,
        )
        if match_obj.finished:
            continue

        match_obj.set_score(match.home_goals, match.away_goals)
        # update stats
        TeamStats.objects.get(
            team__fb_id=match.home_team_id, season=matchweek.season
        ).update_stats(match.home_goals, match.away_goals)
        TeamStats.objects.get(
            team__fb_id=match.away_team_id, season=matchweek.season
        ).update_stats(match.away_goals, match.home_goals)

    if matchweek.matches.filter(finished=True).count() == matchweek.amt_matches:
        matchweek.finished = True
        matchweek.save()
        return check_and_update_currently_matchweek()

    return f"Matchweek: {matchweek.matchweek}"


# TODO sprawdza czy coś zostało zmienione w match i matchweek od aktualnego do końca
