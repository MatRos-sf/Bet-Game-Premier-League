from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.db.models import F

from .models import Match, Matchweek
from bet.models import Bet
from league.models import Team, TeamStats


@receiver(pre_save, sender=Matchweek)
def matchweek_finished(sender, instance, update_fields=None, **kwargs):
    try:
        old_instance = Matchweek.objects.get(id=instance.id)
    except Matchweek.DoesNotExist:
        return

    if not old_instance.finished and instance.finished:
        # check all match is finished
        finished_matches = Match.objects.filter(
            matchweek=old_instance, finished=True
        ).count()

        if old_instance.amt_matches != finished_matches:
            raise ValidationError(
                _("Every matchweek matches must be finished!"), code="invalid"
            )

    # TODO fished may not finish before start date only after end_date


@receiver(pre_save, sender=Matchweek)
def team_points_allocation(sender, instance, update_fields=None, **kwargs):
    try:
        old_instance = Matchweek.objects.get(id=instance.id)
    except Matchweek.DoesNotExist:
        return

    if not old_instance.finished and instance.finished:
        # przyznajemy
        matches = Match.objects.filter(matchweek=old_instance, finished=True)

        for match in matches:
            winner, _ = match.winner

            ts_home = TeamStats.objects.get(
                team=match.home_team, season=match.matchweek.season
            )
            ts_away = TeamStats.objects.get(
                team=match.away_team, season=match.matchweek.season
            )
            if winner == "draw":
                ts_home.played = F("played") + 1
                ts_home.drawn = F("drawn") + 1
                ts_home.goals_for = F("goals_for") + match.home_goals
                ts_home.goals_against = F("goals_against") + match.away_goals
                ts_home.points = F("points") + 1

                ts_away.played = F("played") + 1
                ts_away.drawn = F("drawn") + 1
                ts_away.goals_for = F("goals_for") + match.away_goals
                ts_away.goals_against = F("goals_against") + match.home_goals
                ts_away.points = F("points") + 1

            elif winner == "home":
                ts_home.played = F("played") + 1
                ts_home.won = F("won") + 1
                ts_home.goals_for = F("goals_for") + match.home_goals
                ts_home.goals_against = F("goals_against") + match.away_goals
                ts_home.points = F("points") + 3

                ts_away.played = F("played") + 1
                ts_away.lost = F("lost") + 1
                ts_away.goals_for = F("goals_for") + match.away_goals
                ts_away.goals_against = F("goals_against") + match.home_goals

            else:
                ts_home.played = F("played") + 1
                ts_home.lost = F("lost") + 1
                ts_home.goals_for = F("goals_for") + match.home_goals
                ts_home.goals_against = F("goals_against") + match.away_goals
                ts_home.points = F("points") + 3

                ts_away.played = F("played") + 1
                ts_away.win = F("lost") + 1
                ts_away.goals_for = F("goals_for") + match.away_goals
                ts_away.goals_against = F("goals_against") + match.home_goals
                ts_away.points = F("points") + 3

            ts_home.save()
            ts_away.save()
    elif old_instance.finished and not instance.finished:
        # odejmowanie
        matches = Match.objects.filter(matchweek=old_instance, finished=True)

        for match in matches:
            winner, _ = match.winner

            ts_home = TeamStats.objects.get(
                team=match.home_team, season=match.matchweek.season
            )
            ts_away = TeamStats.objects.get(
                team=match.away_team, season=match.matchweek.season
            )
            if winner == "draw":
                ts_home.played = F("played") - 1
                ts_home.drawn = F("drawn") - 1
                ts_home.goals_for = F("goals_for") - match.home_goals
                ts_home.goals_against = F("goals_against") - match.away_goals
                ts_home.points = F("points") - 1

                ts_away.played = F("played") - 1
                ts_away.drawn = F("drawn") - 1
                ts_away.goals_for = F("goals_for") - match.away_goals
                ts_away.goals_against = F("goals_against") - match.home_goals
                ts_away.points = F("points") - 1

            elif winner == "home":
                ts_home.played = F("played") - 1
                ts_home.won = F("won") - 1
                ts_home.goals_for = F("goals_for") - match.home_goals
                ts_home.goals_against = F("goals_against") - match.away_goals
                ts_home.points = F("points") - 3

                ts_away.played = F("played") - 1
                ts_away.lost = F("lost") - 1
                ts_away.goals_for = F("goals_for") - match.away_goals
                ts_away.goals_against = F("goals_against") - match.home_goals

            else:
                ts_home.played = F("played") - 1
                ts_home.lost = F("lost") - 1
                ts_home.goals_for = F("goals_for") - match.home_goals
                ts_home.goals_against = F("goals_against") - match.away_goals
                ts_home.points = F("points") - 3

                ts_away.played = F("played") - 1
                ts_away.win = F("lost") - 1
                ts_away.goals_for = F("goals_for") - match.away_goals
                ts_away.goals_against = F("goals_against") - match.home_goals
                ts_away.points = F("points") - 3

            ts_home.save()
            ts_away.save()


# TODO przyznanie użytkownikom pkt.
@receiver(post_save, sender=Match)
def check_bets(sender, instance, **kwargs):
    if instance.finished:
        bets = Bet.objects.filter(match=instance)
        for bet in bets:
            bet.winner()
