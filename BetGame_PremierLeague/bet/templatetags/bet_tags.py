from django import template
from bet.models import Bet

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
    return choice_bet.winner() if choice_bet else None


@register.simple_tag
def user_risk(match, user) -> bool:
    try:
        bet = Bet.objects.get(user=user, match=match)
        return bet.risk
    except Bet.DoesNotExist:
        return False
