from requests.exceptions import HTTPError, Timeout
from django.utils import timezone

from match.models import Matchweek, Match
from football_data.premier_league import PremierLeague
from league.models import League, Team, Season, TeamStats
from league.management.commands.pull_fd import Command


def get_previous_season_year() -> int:
    return Season.objects.first().end_date.year


def create_new_season() -> bool:
    new_season = get_previous_season_year()
    pl = PremierLeague()

    if pl.check_new_season(new_season):
        command_instance = Command()
        command_instance.handle()
        return True
    return False


def check_and_update_currently_matchweek() -> str:
    """
    Checks the current matchweek stored in the database and compares it with the data from football-data.api.
    If there are discrepancies, updates the matches and matchweek accordingly.
    :return:
    """
    matchweek = Matchweek.objects.filter(finished=False).first()

    if not matchweek:
        if create_new_season():
            return f"The new season has been created"
        return f"The {matchweek.season.start_date.year } season has ended!"
    elif matchweek.start_date < timezone.now().date():
        return "No changes!"
    elif matchweek.matchweek == matchweek.season.amt_matchweeks and matchweek.finished:
        if create_new_season():
            return f"The new season has been created"
        return f"The {matchweek.season.start_date.year } season has ended!"

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

    if matchweek.is_finished():
        matchweek.finished = True
        matchweek.save()
        return check_and_update_currently_matchweek()

    return f"Matchweek: {matchweek.matchweek}"
