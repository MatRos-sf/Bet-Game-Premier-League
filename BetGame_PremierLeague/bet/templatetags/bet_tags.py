from django import template
from bet.models import Bet

register = template.Library()


@register.simple_tag
def user_bet(**kwargs):
    user = kwargs["user"]
    match = kwargs["match"]
    choice_bet = Bet.objects.filter(user=user, match=match).first()
    return choice_bet.choice if choice_bet else "None"
