from django.test import tag

from league.tests.test_models import SimpleDB
from bet.models import Bet
from bet.factories.model_factory import BetFactory
from match.factories.models_factory import MatchFactory


@tag("bet_model")
class BetTest(SimpleDB):
    def test_should_create_nine_bets(self):
        self.assertEquals(Bet.objects.count(), 9)

    def test_should_create_three_bers_with_risk(self):
        self.assertEquals(Bet.objects.filter(risk=True).count(), 3)

    def test_should_show_pk_when_call_model(self):
        bet = Bet.objects.first()

        self.assertEquals(str(bet), str(bet.pk))
