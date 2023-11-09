from django.test import TestCase, Client, tag
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import auth
from faker import Faker

from users.models import Profile
from http import HTTPStatus
from .factories.user import UserFactory


@tag("register")
class RegisterTest(TestCase):
    def setUp(self):
        self.url = "/register/"
        self.name = "register"
        self.fake = Faker()

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse(self.name))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_uses_correctly_templates(self):
        response = self.client.get(reverse(self.name))

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/register.html")

    def test_post_should_redirect_when_form_is_valid(self):
        fake_password = self.fake.password()
        payload = {
            "username": "user_test",
            "email": self.fake.email(),
            "password1": fake_password,
            "password2": fake_password,
        }
        response = self.client.post(reverse(self.name), data=payload)

        self.assertRedirects(response, reverse("login"))

    def test_post_should_show_messages_when_form_is_valid(self):
        fake_password = self.fake.password()
        payload = {
            "username": "user_test",
            "email": self.fake.email(),
            "password1": fake_password,
            "password2": fake_password,
        }

        response = self.client.post(reverse(self.name), data=payload, follow=True)
        expected_message = (
            f"Dear {payload['username']}, you have been successfully signed up!"
        )

        message = list(response.context.get("messages"))[0]
        self.assertEquals(message.tags, "success")
        self.assertEquals(expected_message, message.message)

    def test_post_should_create_user_and_profile_when_form_is_valid(self):
        payload = {
            "username": "test",
            "email": "test@test.pl",
            "password1": "{5:vhM9Ed[M/VmL",
            "password2": "{5:vhM9Ed[M/VmL",
        }

        self.client.post(reverse("register"), data=payload, follow=True)

        self.assertTrue(User.objects.get(username=payload["username"]))
        self.assertTrue(Profile.objects.get(user__username=payload["username"]))

    def test_post_should_not_create_user_and_profile_when_form_is_invalid(self):
        payload = {
            "username": "test",
            "password1": self.fake.password(),
            "password2": self.fake.password(),
        }

        self.client.post(reverse(self.name), data=payload, follow=True)

        self.assertFalse(User.objects.filter(username=payload["username"]).exists())
        self.assertFalse(
            Profile.objects.filter(user__username=payload["username"]).exists()
        )

    def test_user_should_be_logout_when_create_new_account(self):
        user = UserFactory()
        self.client.login(username=user.username, password="1_test_TEST_!")  # nosec
        response = self.client.get(reverse("register"))

        expected_message = f"Dear {user.username}, you have been successfully log out!"
        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.tags, "info")
        self.assertEquals(expected_message, message.message)


class LoginViewTest(TestCase):
    pass


class LogoutView(TestCase):
    pass


from unittest.mock import patch
from pprint import pprint


@tag("user_home")
class HomeTest(TestCase):
    def setUp(self):
        self.url = ""
        self.name = "home"
        self.fake = Faker()

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse(self.name))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_uses_correctly_templates(self):
        response = self.client.get(reverse(self.name))

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/home_page.html")

    def test_should_context_empty_when_db_is_empty(self):
        response = self.client.get(reverse(self.name))

        self.assertFalse(response.context["amt_users"])
        self.assertFalse(response.context["table"])
        self.assertFalse(response.context["last_match"])
        self.assertFalse(response.context["next_match"])
        self.assertFalse(response.context["last_bets"])
        self.assertFalse(response.context["top_players"])

    # def test_should_the_same_context_when_user_is_authenticated_or_is_not(self):
    #     user = User.objects.create(username='test', password='xD8J4emu8U7mYg1')
    #     credentials = {
    #         'username': user.username,
    #         'password': user.password
    #     }
    #     self.client.login(**credentials, follow=True)

    #     print(response.context['user'])
    #     print(a.status_code)

    # with patch('django.contrib.auth.models.User.objects.count', return_value=200):
    #     response = self.client.get(reverse(self.name))
    #
    #     print(response.context['amt_users'])


@tag("xD")
class ProfileDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="test", password="gyBf4kSXb98QUSt")  # nosec

    def setUp(self):
        self.name = "profile-detail"
        self.url = lambda x: f"/profile/{x}/"

        self.sample_user = User.objects.get(pk=1)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(
            reverse(self.name, kwargs={"slag": self.sample_user.username})
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)

    def test_view_url_exist_at_desired_location_2(self):
        u = UserFactory()
        is_done = self.client.login(
            username=u.username, password="IhT5JiLnWC7VfrA"
        )  # nosec

        response = self.client.get(
            reverse(self.name, kwargs={"slag": self.sample_user.username})
        )
        # self.assertEquals(response.status_code, HTTPStatus.OK)
        print(is_done)

    # def test_view_url_accessible_by_name(self):
    #     response = self.client.get(reverse(self.name))
    #     self.assertEquals(response.status_code, HTTPStatus.OK)
    #
    # def test_view_uses_correctly_templates(self):
    #     response = self.client.get(reverse(self.name))

    # https://realpython.com/testing-in-django-part-2-model-mommy-vs-django-testing-fixtures/
