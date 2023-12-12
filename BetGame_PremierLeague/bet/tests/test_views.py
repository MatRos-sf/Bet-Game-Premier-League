from datetime import timedelta
from unittest import mock

from django.test import tag, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from league.tests.test_models import SimpleDB
from bet.models import Bet
from match.models import Match, Matchweek


class UserFinishedBetsListViewTest(SimpleDB):
    def setUp(self):
        self.url = "bet-finished"
        self.sample_user = User.objects.first()

    def test_should_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url), follow=True)
        self.assertRedirects(response, f"/login/?next={reverse(self.url)}")

    def test_should_return_3_bets(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url), follow=True)

        context = response.context["object_list"]
        self.assertEquals(len(context), 3)


@tag("bet_view")
class BetsListViewWhenMatchweekStartTest(SimpleDB):
    def setUp(self):
        self.url = "bet-home"
        self.sample_user = User.objects.first()

    def test_should_redirect_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url), follow=True)
        self.assertRedirects(response, f"/login/?next={reverse(self.url)}")

    def test_should_return_appropriate_context(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.url))

        context = response.context

        self.assertEquals(context["matches"].count(), 2)
        self.assertEquals(context["matchweek"].matchweek, 4)
        self.assertTrue(context["is_started"])
        self.assertFalse(context["finished_matches"])

    @mock.patch("match.models.Matchweek.objects")
    def test_should_have_end_season_in_the_context(self, mock_matchweek):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        mock_matchweek.filter.return_value.first.return_value = None
        response = self.client.get(reverse(self.url))

        self.assertTrue(response.context["end_season"])
