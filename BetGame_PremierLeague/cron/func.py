from deployment.management.commands.pull_fd import Command
from django.utils import timezone
from football_data.premier_league import PremierLeague
from league.models import Season, TeamStats
from match.models import Match, Matchweek
from requests.exceptions import HTTPError, Timeout


def get_previous_season_year() -> int:
    return Season.objects.first().end_date.year


def create_new_season() -> bool:
    new_season = get_previous_season_year()
    league = PremierLeague()

    if league.check_new_season(new_season):
        command_instance = Command()
        command_instance.handle()
        return True
    return False


def check_and_update_currently_matchweek() -> str:
    """
    Checks the current matchweek stored in the database and compares it with the data from football-data.api.
    If there are discrepancies, updates the matches and matchweek accordingly.
    """
    matchweek = Matchweek.objects.filter(finished=False, cancelled=False).first()

    if not matchweek:
        if create_new_season():
            return "The new season has been created"
        return f"The {matchweek.season.start_date.year } season has ended!"
    elif timezone.now().date() < matchweek.start_date:
        return "No changes!"
    elif matchweek.matchweek == matchweek.season.amt_matchweeks and matchweek.finished:
        if create_new_season():
            return "The new season has been created"
        return f"The {matchweek.season.start_date.year } season has ended!"

    league = PremierLeague()

    try:
        finished_matches = league.update_score_matches(matchweek.matchweek)
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

        if match.cancelled:
            match_obj.cancelled = True
            match_obj.save()

        elif not match.finished:
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
    elif matchweek.matches.count() == matchweek.matches.filter(cancelled=True).count():
        matchweek.cancelled = True
        matchweek.save()
        return check_and_update_currently_matchweek()

    return f"Matchweek: {matchweek.matchweek}"


def check_and_update_cancelled_matches() -> str:
    matches = Match.objects.filter(cancelled=True)

    league = PremierLeague()
    count = 0
    for match in matches:
        score = league.check_match(
            match.matchweek.start_date.year,
            match.matchweek.matchweek,
            match.home_team.fb_id,
            match.away_team.fb_id,
        )
        if score:
            match.set_score(score["home"], score["away"])
            count += 1

    return f"Update {count} matches!"
