from django.test import TestCase, tag
from django.urls import reverse
from django.contrib.auth.models import User
from faker import Faker
from http import HTTPStatus

from users.models import Profile
from users.forms import ProfileUpdateForm
from ..factories.user import UserFactory
from league.factories.models_factory import (
    TeamStatsFactory,
    LeagueFactory,
    SeasonFactory,
    TeamFactory,
)
from match.factories.models_factory import MatchweekFactory, MatchFactory
from league.models import League, TeamStats


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


class LoginViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(LoginViewTest, cls).setUpClass()
        UserFactory()

    def setUp(self):
        self.url = "/login/"
        self.name = "login"

        self.user = User.objects.first()

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

    def test_should_not_login_when_form_invalid(self):
        payload = {"username": self.user.username, "password": ""}
        response = self.client.post(reverse(self.name), data=payload, follow=True)

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertEquals(response.status_code, HTTPStatus.OK)


class LogoutView(TestCase):
    @classmethod
    def setUpClass(cls):
        super(LogoutView, cls).setUpClass()
        UserFactory()

    def setUp(self):
        self.url = "/logout/"
        self.name = "logout"

        self.user = User.objects.first()

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

    def test_context_table_should_show_only_eight_first_positions_when_teamstats_has_more_than_eight_instance(
        self,
    ):
        league = LeagueFactory()
        season = SeasonFactory(league=league)
        TeamStatsFactory.create_batch(10, season=season)

        response = self.client.get(reverse(self.name))
        table = response.context["table"]

        self.assertEquals(League.objects.count(), 1)
        self.assertEquals(TeamStats.objects.count(), 10)

        self.assertEquals(len(table), 8)

    def test_context_should_get_last_ended_match(self):
        season = SeasonFactory()
        mw = MatchweekFactory(season=season, finished=True)
        match = MatchFactory(matchweek=mw, home_goals=1, away_goals=2, finished=True)

        response = self.client.get(reverse(self.name))
        last_match = response.context["last_match"]

        self.assertEquals(last_match, match)


class ProfileDetailViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileDetailViewTest, cls).setUpClass()
        UserFactory()
        UserFactory()

    def setUp(self):
        self.name = "profile-detail"
        self.url = lambda x: f"/profile/{x}/"

        self.user_one = User.objects.first()
        self.user_two = User.objects.last()

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        username = self.user_one.username
        response = self.client.get(self.url(username))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self):
        self.client.login(
            username=self.user_one.username, password="1_test_TEST_!"
        )  # nosec

        response = self.client.get(self.url(self.user_one.username))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_inaccessible_by_name_when_user_is_not_authenticated(self):
        username = self.user_one.username

        response = self.client.get(reverse(self.name, kwargs={"slag": username}))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    def test_view_url_accessible_by_name_when_user_is_authenticated(self):
        username = self.user_one.username
        self.client.login(
            username=self.user_one.username, password="1_test_TEST_!"
        )  # nosec
        response = self.client.get(reverse(self.name, kwargs={"slag": username}))

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_uses_should_correctly_templates_when_user_is_authenticated(self):
        username = self.user_one.username
        self.client.login(
            username=self.user_one.username, password="1_test_TEST_!"
        )  # nosec

        response = self.client.get(reverse(self.name, kwargs={"slag": username}))

        self.assertTemplateUsed(response, "users/profile.html")

    def test_user_can_watch_different_users_when_is_authenticated(self):
        username = self.user_one.username
        self.client.login(username=username, password="1_test_TEST_!")  # nosec

        response = self.client.get(
            reverse(self.name, kwargs={"slag": self.user_two.username})
        )

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_status_not_found_when_user_want_to_get_non_exist_profile(self):
        username = self.user_one.username
        self.client.login(username=username, password="1_test_TEST_!")  # nosec

        response = self.client.get(reverse(self.name, kwargs={"slag": "non_user"}))

        self.assertEquals(response.status_code, HTTPStatus.NOT_FOUND)


class ProfileListViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileListViewTest, cls).setUpClass()
        UserFactory.create_batch(10)

    def setUp(self):
        self.name = "profile-list"
        self.url = "/profiles/"

        self.sample_user = User.objects.all().first()

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_inaccessible_by_name_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.name))

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_accessible_by_name_when_user_is_authenticated(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.name))

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_none_object_list_when_user_did_use_search(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(reverse(self.name))
        object_list = response.context["object_list"]
        self.assertFalse(object_list)

    def test_should_object_list_when_user_used_search(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(self.url + "?username=user")
        object_list = response.context["object_list"]
        self.assertTrue(object_list)
        self.assertEquals(len(object_list), 10)

    def test_show_message_when_user_not_found(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(self.url + "?username=xxx")

        expected_message = "User not found!"
        message = list(response.context.get("messages"))[0]

        self.assertTrue(message.tags == "info")
        self.assertTrue(message.message == expected_message)


class EditProfileTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(EditProfileTest, cls).setUpClass()
        UserFactory()

    def setUp(self):
        self.sample_user = User.objects.get(id=1)

        self.name = "profile-edit"
        self.url = lambda username: f"/profile/{username}/edit/"

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        username = self.sample_user.username
        response = self.client.get(self.url(username))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url(self.sample_user.username))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_view_url_inaccessible_by_name_when_user_is_not_authenticated(self):
        username = self.sample_user.username
        response = self.client.get(reverse(self.name, kwargs={"username": username}))

        self.assertRedirects(response, f"/login/?next={self.url(username)}")

    def test_view_url_accessible_by_name_when_user_is_authenticated(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        username = self.sample_user.username
        response = self.client.get(reverse(self.name, kwargs={"username": username}))

        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_message_when_user_try_update_sb_profile(self):
        user = UserFactory()
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(
            reverse(self.name, kwargs={"username": user.username}), follow=True
        )

        expected_message = "You can only update own profile!"
        message = list(response.context.get("messages"))[0]

        self.assertEquals(message.message, expected_message)
        self.assertEquals(message.tags, "warning")

    def test_should_give_appropriate_form(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        username = self.sample_user.username
        response = self.client.get(reverse(self.name, kwargs={"username": username}))
        self.assertIsInstance(response.context["form"], ProfileUpdateForm)

    def test_post_should_change_description(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        username = self.sample_user.username

        payload = {"description": "new_description"}

        self.client.post(
            reverse(self.name, kwargs={"username": username}), data=payload
        )

        self.assertEquals(self.sample_user.profile.description, payload["description"])
        self.assertFalse(self.sample_user.profile.support_team)

    def test_post_should_set_new_support_team(self):
        team = TeamFactory()
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        username = self.sample_user.username

        payload = {"support_team": team.pk}

        self.client.post(
            reverse(self.name, kwargs={"username": username}), data=payload
        )

        self.assertEquals(self.sample_user.profile.support_team, team)
