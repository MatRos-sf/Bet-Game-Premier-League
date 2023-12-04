from django import template
from bet.models import Bet
from django.db.models import QuerySet
from typing import Tuple, Union
from django.contrib.auth.models import User
from datetime import timedelta

from match.models import Matchweek, Match

register = template.Library()


@register.simple_tag
def user_bet(**kwargs):
    user = kwargs["user"]
    match = kwargs["match"]
    choice_bet = Bet.objects.filter(user=user, match=match).first()
    return choice_bet.choice if choice_bet else "None"


@register.simple_tag
def user_check_bet(**kwargs):
    user = kwargs["user"]
    match = kwargs["match"]
    choice_bet = Bet.objects.filter(user=user, match=match).first()
    return choice_bet.check_bet() if choice_bet else None


@register.simple_tag
def user_risk(match, user) -> bool:
    """
    The tag which check if user has bet with risk.
    """
    try:
        bet = Bet.objects.get(user=user, match=match)
        return bet.risk
    except Bet.DoesNotExist:
        return False


@register.simple_tag
def get_user_matchweek_bets(user: User, matchweek: Matchweek) -> QuerySet[dict]:
    fields = ("match_id", "risk", "choice")
    bets = (
        Bet.objects.filter(user=user, match__matchweek=matchweek)
        .select_related("match")
        .values(*fields)
    )
    return bets


@register.simple_tag
def check_user_choice(
    match_id: int, bets: QuerySet[dict]
) -> Union[Tuple[str, bool], Tuple[None, None]]:
    """
    Get the user's bet details: the choice and risk.

    Returns Tuple[None, None] if user's has not a bet!
    """
    bet = list(filter(lambda x: x["match_id"] == match_id, bets))
    try:
        bet = bet[0]
    except IndexError:
        return None, None
    else:
        return bet["choice"], bet["risk"]


@register.simple_tag
def is_match_instance(instance) -> bool:
    return isinstance(instance, Match)
