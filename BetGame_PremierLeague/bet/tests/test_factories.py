from django.test import TestCase
from django.contrib.auth.models import User

from ..factories.model_factory import BetFactory
from bet.models import Bet
from league.models import Team
from match.models import Match, Matchweek
from users.models import Profile


class BetFactoryTest(TestCase):
    def test_should_created_bet(self):
        BetFactory()
        self.assertEquals(User.objects.count(), 1)
        self.assertEquals(Profile.objects.count(), 1)
        self.assertEquals(Match.objects.count(), 1)
        self.assertEquals(Matchweek.objects.count(), 1)
        self.assertEquals(Bet.objects.count(), 1)
        self.assertEquals(Team.objects.count(), 2)
