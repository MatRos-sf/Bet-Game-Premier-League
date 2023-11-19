from factory.django import DjangoModelFactory
from factory import Sequence, Faker, SubFactory


from bet.models import Bet
from users.tests.factories.user import UserFactory
from match.tests.factories.models_factory import MatchFactory


class BetFactory(DjangoModelFactory):
    class Meta:
        model = Bet

    match = SubFactory(MatchFactory)
    user = SubFactory(UserFactory)
    choice = "home"
    risk = False
