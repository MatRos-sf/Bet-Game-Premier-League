from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.urls import reverse
from http import HTTPStatus
from parameterized import parameterized

from league.tests.test_models import SimpleDB


class UserListViewTest(SimpleDB):
    def setUp(self):
        self.client = APIClient()
        for user in User.objects.all():
            Token.objects.create(user=user)

        self.user_sample = User.objects.first()
        self.user_token_sample = Token.objects.get(user=self.user_sample)

    def test_should_create_token(self):
        self.assertEquals(User.objects.count(), 3)
        self.assertEquals(Token.objects.count(), 3)

    @parameterized.expand([0, 1, 2])
    def test_should_show_user_list_when_user_is_authenticated(self, index):
        token = Token.objects.all()[index]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(reverse("api:users"))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    @parameterized.expand([0, 1, 2])
    def test_should_show_show_401_when_user_did_not_write_token_in_authorization(
        self, index
    ):
        token = Token.objects.all()[index]
        self.client.credentials(HTTP_AUTHORIZATION=token.key)
        response = self.client.get(reverse("api:users"))
        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_should_show_401_when_user_is_unauthorized(self):
        response = self.client.get(reverse("api:users"))

        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEquals(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_should_response_key_key(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.user_token_sample.key
        )
        response = self.client.get(reverse("api:users"))
        response_data = response.data
        self.assertTrue(response_data.get("count", False))
        self.assertTrue(response_data.get("users", False))

    def test_should_response_three_users(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.user_token_sample.key
        )
        response = self.client.get(reverse("api:users"))
        response_data = response.data

        expected = User.objects.count()
        self.assertEquals(response_data.get("count"), expected)
        self.assertEquals(len(response_data.get("users")), expected)


class ProfileViewTest(SimpleDB):
    def setUp(self):
        self.client = APIClient()
        for user in User.objects.all():
            Token.objects.create(user=user)

        self.user_sample = User.objects.first()
        self.user_token_sample = Token.objects.get(user=self.user_sample)

        self.url = lambda username: reverse(
            "api:profile", kwargs={"user__username": username}
        )

    def test_should_create_token(self):
        self.assertEquals(User.objects.count(), 3)
        self.assertEquals(Token.objects.count(), 3)

    @parameterized.expand([0, 1, 2])
    def test_should_show_profile_info_when_user_is_authenticated(self, index):
        token = Token.objects.all()[index]
        user = User.objects.all()[index]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(self.url(user.username))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_show_401_when_user_is_unauthorized(self):
        response = self.client.get(self.url(self.user_sample.username))

        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEquals(
            response.data["detail"], "Authentication credentials were not provided."
        )

    def test_should_response_keys(self):
        expected_key = {"description", "url", "points", "user"}
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.user_token_sample.key
        )
        response = self.client.get(self.url(self.user_sample.username))
        response_data = {key for key in response.data.keys()}

        self.assertEquals(response_data, expected_key)


class BetViewTest(SimpleDB):
    def setUp(self):
        self.client = APIClient()
        for user in User.objects.all():
            Token.objects.create(user=user)

        self.user_sample = User.objects.first()
        self.user_token_sample = Token.objects.get(user=self.user_sample)

        self.url = lambda username: reverse(
            "api:bet", kwargs={"user__username": username}
        )

    @parameterized.expand([0, 1, 2])
    def test_should_show_bet_info_when_user_is_authenticated(self, index):
        token = Token.objects.all()[index]
        user = User.objects.all()[index]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
        response = self.client.get(self.url(user.username))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_show_401_when_user_is_unauthorized(self):
        response = self.client.get(self.url(self.user_sample.username))

        self.assertEquals(response.status_code, HTTPStatus.UNAUTHORIZED)
        self.assertEquals(
            response.data["detail"], "Authentication credentials were not provided."
        )

    # def test_should_be_one_query(self):
    #     self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token_sample.key)
    #     with self.assertNumQueries(3):
    #         self.client.get(self.url(self.user_sample.username))

    def test_should_response_keys(self):
        expected_key = {"count", "bets"}
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.user_token_sample.key
        )
        response = self.client.get(self.url(self.user_sample.username))
        response_data = {key for key in response.data.keys()}

        self.assertEquals(response_data, expected_key)
