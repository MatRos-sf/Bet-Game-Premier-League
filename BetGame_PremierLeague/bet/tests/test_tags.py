from django.test import tag, TestCase
from django.contrib.auth.models import User
from django.db.models import QuerySet
from parameterized import parameterized

from bet.models import Bet
from match.models import Matchweek
from league.tests.test_models import SimpleDB
from bet.templatetags.bet_tags import get_user_matchweek_bets, check_user_choice


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


@tag("get_user_matchweek_bets")
class CheckUserChoiceTest(TestCase):
    @parameterized.expand(
        [
            (
                139,
                (
                    {"match_id": 139, "risk": False, "choice": "away"},
                    {"match_id": 141, "risk": True, "choice": "draw"},
                ),
                ("away", False),
            ),
            (
                139,
                (
                    {"match_id": 139, "risk": False, "choice": "draw"},
                    {"match_id": 139, "risk": True, "choice": "away"},
                ),
                ("draw", False),
            ),
        ]
    )
    def test_should_return_tumple(self, match_id, bets, expected):
        response = check_user_choice(match_id, bets)

        self.assertEquals(expected[0], response[0])
        self.assertEquals(expected[1], response[1])

    @parameterized.expand(
        [(1, ()), (130, ({"match_id": 139, "risk": False, "choice": "away"},))]
    )
    def test_should_return_none_tuple_when_user_does_not_any_bets_or_does_not_particular_bet(
        self, match_id, bets
    ):
        response = check_user_choice(match_id, bets)

        self.assertFalse(response[0])
        self.assertFalse(response[1])
