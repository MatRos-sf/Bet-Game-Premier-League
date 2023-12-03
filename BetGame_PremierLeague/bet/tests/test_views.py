from django.test import tag
from django.contrib.auth.models import User
from django.urls import reverse
from http import HTTPStatus

from league.tests.test_models import SimpleDB
from bet.models import Bet
from match.models import Match


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

    def test_should_not_create_bet_when_matchweek_has_been_started(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        number_of_bets_before_post = Bet.objects.filter(user=self.sample_user).count()
        expected_message = (
            "You cannot create bet because the matchweek has been started!"
        )
        response = self.client.post(reverse(self.url), data={"bet": "home 7"})

        message = list(response.context["messages"])[0]
        self.assertEquals(
            number_of_bets_before_post,
            Bet.objects.filter(user=self.sample_user).count(),
        )
        self.assertEquals(message.tags, "info")
        self.assertEquals(message.message, expected_message)
