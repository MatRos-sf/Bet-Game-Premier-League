from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth.models import User
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
        self.assertTemplateUsed(response, "users/form.html")

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


@tag("login")
class LoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory()

    def setUp(self):
        self.url = "/login/"
        self.name = "login"

        self.user = User.objects.get(id=1)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse(self.name))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_uses_correctly_templates(self):
        response = self.client.get(reverse(self.name))

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/form.html")

    def test_should_login_when_form_valid(self):
        payload = {"username": self.user.username, "password": "1_test_TEST_!"}
        response = self.client.post(reverse(self.name), data=payload, follow=True)

        self.assertRedirects(response, reverse("bet-home"))
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_should_not_login_when_form_invalid(self):
        payload = {"username": self.user.username, "password": ""}
        response = self.client.post(reverse(self.name), data=payload, follow=True)

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertEquals(response.status_code, HTTPStatus.OK)


@tag("logout")
class LogoutView(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory()

    def setUp(self):
        self.url = "/logout/"
        self.name = "logout"

        self.user = User.objects.get(id=1)

    def test_view_url_exist_at_desired_location(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse(self.name))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_uses_correctly_templates(self):
        response = self.client.get(reverse(self.name))

        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/logout.html")

    def test_should_logout_user_when_was_login(self):
        is_login = self.client.login(
            username=self.user.username, password="1_test_TEST_!"  # nosec
        )
        self.assertTrue(is_login)

        response = self.client.get(reverse(self.name))
        self.assertFalse(response.context["user"].is_authenticated)


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


@tag("profile")
class ProfileDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory()
        UserFactory()

    def setUp(self):
        self.name = "profile-detail"
        self.url = lambda x: f"/profile/{x}/"

        self.user_one = User.objects.get(pk=1)
        self.user_two = User.objects.get(pk=2)

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        username = self.user_one.username
        response = self.client.get(self.url(username))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    # def test_view_url_exist_at_desired_location_when_user_is_authenticated(self):
    #     self.client.login(
    #         username=self.user_one.username, password="1_test_TEST_!"
    #     )  # nosec
    #
    #     response = self.client.get(self.url(self.user_one.username))
    #     self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_inaccessible_by_name_when_user_is_not_authenticated(self):
        username = self.user_one.username

        response = self.client.get(reverse(self.name, kwargs={"slag": username}))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    # def test_view_url_accessible_by_name_when_user_is_authenticated(self):
    #     username = self.user_one.username
    #     self.client.login(
    #         username=self.user_one.username, password="1_test_TEST_!"
    #     )  # nosec
    #     response = self.client.get(reverse(self.name, kwargs={"slag": username}))
    #
    #     self.assertEquals(response.status_code, HTTPStatus.OK)

    # def test_view_uses_should_correctly_templates_when_user_is_authenticated(self):
    #     username = self.user_one.username
    #     self.client.login(
    #         username=self.user_one.username, password="1_test_TEST_!"
    #     )  # nosec
    #
    #     response = self.client.get(reverse(self.name, kwargs={"slag": username}))
    #
    #     self.assertTemplateUsed(response, "users/profile.html")
    #
    # def test_user_can_watch_different_users_when_is_authenticated(self):
    #     username = self.user_one.username
    #     self.client.login(username=username, password="1_test_TEST_!")  # nosec
    #
    #     response = self.client.get(
    #         reverse(self.name, kwargs={"slag": self.user_two.username})
    #     )
    #
    #     self.assertEquals(response.status_code, HTTPStatus.OK)
    #
    # def test_should_status_not_found_when_user_want_to_get_non_exist_profile(self):
    #     username = self.user_one.username
    #     self.client.login(username=username, password="1_test_TEST_!")  # nosec
    #
    #     response = self.client.get(reverse(self.name, kwargs={"slag": "non_user"}))
    #
    #     self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)

    # def test_view_url_exist_at_desired_location_2(self):
    #     u = UserFactory()
    #     is_done = self.client.login(
    #         username=u.username, password="IhT5JiLnWC7VfrA"
    #     )  # nosec
    #
    #     response = self.client.get(
    #         reverse(self.name, kwargs={"slag": self.sample_user.username})
    #     )
    #     # self.assertEquals(response.status_code, HTTPStatus.OK)
    #     print(is_done)

    # def test_view_url_accessible_by_name(self):
    #     response = self.client.get(reverse(self.name))
    #     self.assertEquals(response.status_code, HTTPStatus.OK)
    #
    # def test_view_uses_correctly_templates(self):
    #     response = self.client.get(reverse(self.name))

    # https://realpython.com/testing-in-django-part-2-model-mommy-vs-django-testing-fixtures/
