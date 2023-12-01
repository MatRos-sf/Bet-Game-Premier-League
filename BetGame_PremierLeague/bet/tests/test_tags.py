from django.test import tag
from django.contrib.auth.models import User

from bet.models import Bet
from match.models import Matchweek
from league.tests.test_models import SimpleDB
from bet.templatetags.bet_tags import get_user_matchweek_bets


@tag("get_user_matchweek_bets")
class GetUserMatchweekBetTest(SimpleDB):
    def setUp(self):
        self.user_sample = User.objects.last()
        self.matchweek = Matchweek.objects.first()

    def test_should_return_queryset_dict_with_information_about_match_when_user_took_bets(
        self,
    ):
        result = get_user_matchweek_bets(self.user_sample, self.matchweek)
        self.assertEquals(result.filter(risk=False).count(), 2)
        self.assertEquals(result.count(), 2)

    def test_should_return_empty_qs_when_user_did_took_any_bets(self):
        result = get_user_matchweek_bets(self.user_sample, Matchweek.objects.last())

        self.assertFalse(result.exists())
