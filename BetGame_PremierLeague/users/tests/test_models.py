from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import File
from django.conf import settings
from django.test import tag
from parameterized import parameterized
from PIL import Image
from io import BytesIO
from typing import Tuple
import os
import string
from random import randint, choices

from users.models import Profile, UserScores
from league.models import Team
from ..factories import (
    SimpleProfileFactory,
    ProfileFactory,
    ExtendProfileFactory,
    UserFactory,
    UserScoresFactory,
)


def get_random_name(suffix: str) -> str:
    """
    Generate random name
    """
    letters = string.ascii_letters + string.digits
    name = "".join(choices(letters, k=randint(5, 10)))

    return name + suffix


def get_temporary_image(size: Tuple[int, int], name: str) -> File:
    """
    Generate temporay image

    """
    name = name if name.endswith(".jpg") else name + ".jpg"
    file_obj = BytesIO()
    color = (256, 0, 0)
    image = Image.new("RGB", size=size, color=color)
    image.save(file_obj, format="JPEG")

    file_obj.seek(0)

    return File(file_obj, name=name)


@tag("12a")
class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_one = UserFactory.create(username="JanTest")
        user_two = UserFactory.create(username="OlaTest")

        UserScoresFactory.create(profile=user_one.profile, points=100)
        UserScoresFactory.create(profile=user_one.profile)
        UserScoresFactory.create(profile=user_two.profile, points=1000)

    def setUp(self) -> None:
        self.profile = Profile.objects.get(id=1)

    def test_amt_profiles_should_return_two(self):
        amt_profile = Profile.objects.count()
        self.assertEquals(amt_profile, 2)

    def test_user_field_should_one_to_one_with_user(self):
        user = User.objects.get(id=1)
        self.assertEquals(user, self.profile.user)

    def test_image_label(self):
        field_label = self.profile._meta.get_field("image").verbose_name
        self.assertEquals(field_label, "profile picture")

    def test_should_set_default_image_when_profile_is_create(self):
        expected = "/media/default.jpg"

        self.assertEquals(self.profile.image.url, expected)

    @parameterized.expand([(30, 301, 300), (250, 312, 300), (250, 550, 300)])
    def test_should_set_new_default_image_height_when_image_is_too_height(
        self, width, height, expected
    ):
        name = get_random_name(".jpg")
        pic = get_temporary_image((width, height), name)
        self.profile.image = pic
        self.profile.save()

        self.assertEquals(self.profile.image.name, "profile_pics/" + name)
        self.assertLessEqual(self.profile.image.width, expected)
        self.assertEquals(self.profile.image.height, expected)

        os.remove(os.path.join(settings.BASE_DIR, "media", "profile_pics", name))

    @parameterized.expand([(301, 21, 300), (350, 268, 300), (885, 20, 300)])
    def test_should_set_new_default_width_image_when_image_is_too_width(
        self, width, height, expected
    ):
        name = get_random_name(".jpg")
        pic = get_temporary_image((width, height), name)
        self.profile.image = pic
        self.profile.save()

        self.assertEquals(self.profile.image.name, "profile_pics/" + name)
        self.assertLessEqual(self.profile.image.height, expected)
        self.assertEquals(self.profile.image.width, expected)
        os.remove(os.path.join(settings.BASE_DIR, "media", "profile_pics", name))

    @parameterized.expand([(301, 301, 300), (301, 350, 300), (885, 952, 300)])
    def test_should_set_new_default_image_size_when_sizes_is_too_big(
        self, width, height, expected
    ):
        name = get_random_name(".jpg")
        pic = get_temporary_image((width, height), name)
        self.profile.image = pic
        self.profile.save()

        self.assertLessEqual(self.profile.image.width, expected)
        self.assertLessEqual(self.profile.image.height, expected)

        os.remove(os.path.join(settings.BASE_DIR, "media", "profile_pics", name))

    @parameterized.expand([(55, 200), (150, 150), (1, 1), (110, 210), (300, 300)])
    def test_should_set_original_image_size(self, width, height):
        name = get_random_name(".jpg")
        pic = get_temporary_image((width, height), name)
        self.profile.image = pic
        self.profile.save()

        self.assertEquals(self.profile.image.width, width)
        self.assertEquals(self.profile.image.height, height)

        os.remove(os.path.join(settings.BASE_DIR, "media", "profile_pics", name))

    @parameterized.expand([301, 325, 3000])
    def test_image_field_with_factory_boy_should_set_new_default_image_height_when_image_is_too_height(
        self, height
    ):
        p = ExtendProfileFactory.create(image__height=height)

        self.assertLessEqual(p.image.height, height)
        os.remove(os.path.join(p.image.path))

    @parameterized.expand([301, 325, 3000])
    def test_image_field_with_factory_boy_should_set_new_default_width_image_when_image_is_too_width(
        self, width
    ):
        p = ExtendProfileFactory.create(image__height=width)

        self.assertLessEqual(p.image.height, width)
        os.remove(os.path.join(p.image.path))

    def test_following_field_should_add_new_user(self):
        user_one = User.objects.get(id=1)
        user_two = User.objects.get(id=2)

        p = ExtendProfileFactory.create(following=(user_one, user_two))

        self.assertTrue(p.following)
        self.assertIn(user_one, p.following.all())
        self.assertEquals(p.following.count(), 2)
        os.remove(p.image.path)

    def test_following_field_should_following_be_empty_when_created(self):
        profile_obj = ExtendProfileFactory.create()

        self.assertEquals(profile_obj.following.count(), 0)

        os.remove(profile_obj.image.path)

    def test_support_team_field_should_none_when_create_profile(self):
        profile_obj = SimpleProfileFactory.create()
        self.assertIsNone(profile_obj.support_team)

    def test_support_team_field_should_set_team_when_user_set_it(self):
        profile_obj = ExtendProfileFactory.create()
        self.assertTrue(profile_obj.support_team)

        team = Team.objects.get(id=1)
        self.assertEqual(team.fb_id, profile_obj.support_team.fb_id)

        os.remove(profile_obj.image.path)

    def test_get_absolute_url(self):
        expected = "/profile/JanTest/"
        self.assertEquals(self.profile.get_absolute_url(), expected)

    def test_object_name_is_username(self):
        expected_obj_name = f"{self.profile.user}"
        self.assertEquals(str(self.profile), expected_obj_name)

    def test_user_pk_one_should_have_110_points(self):
        self.assertEquals(self.profile.all_points, 110)

    def test_user_pk_one_should_have_less_points_than_user_pk_two(self):
        points_user_one = self.profile.all_points
        points_user_two = User.objects.get(id=2).profile.all_points

        self.assertLess(points_user_one, points_user_two)

    def test_should_return_only_themselves_qs_when_user_not_add_any_followers(self):
        qs_of_users_who_follow = Profile.followers(user=self.profile.user)
        self.assertEquals(qs_of_users_who_follow.count(), 1)

    def test_should_return_two_followers_when_some_users_following_them(self):
        profile_user = ProfileFactory.create()

        profile_test = ProfileFactory.create(following=(profile_user.user,))
        ProfileFactory.create(following=(profile_user.user,))

        qs_of_users_who_follow = Profile.followers(profile_user.user)

        self.assertTrue(qs_of_users_who_follow)
        self.assertEquals(qs_of_users_who_follow.count(), 2)
        self.assertTrue(qs_of_users_who_follow.filter(user=profile_test.user))

    def test_should_unfollow_user(self):
        profile_user = ProfileFactory.create()

        profile_test = ProfileFactory.create(following=(profile_user.user,))
        ProfileFactory.create(following=(profile_user.user,))

        profile_test.unfollow(profile_user.user.pk)

        qs_of_users_who_follow = Profile.followers(profile_user.user)

        self.assertTrue(qs_of_users_who_follow)
        self.assertEquals(qs_of_users_who_follow.count(), 1)

    def test_should_follow_new_user(self):
        profile_user = ProfileFactory.create()

        profile_test = ProfileFactory.create()

        profile_test.follow(profile_user.user.pk)

        self.assertTrue(profile_user.user in profile_test.following.all())

    def test_position_should_first_position_user_pk_two(self):
        profile_user_two = User.objects.get(id=2)
        position = Profile.position(profile_user_two.username)
        self.assertEquals(position, 1)
        self.assertIsInstance(position, int)

    def test_top_players_should_retrieve_the_best_player(self):
        top_player = Profile.top_players(5)
        profile = Profile.objects.get(id=2)

        self.assertEquals(top_player[0], profile)
        self.assertEquals(top_player[0].sum_points, 1000)

    @parameterized.expand([0, -1, -22])
    def test_top_players_should_raise_valueError_when_value_end_is_lower_1(self, end):
        with self.assertRaises(ValueError):
            Profile.top_players(end)


@tag("model_user_scores")
class UserScoresTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # set 3 users
        user_one = UserFactory.create(username="JanTest")
        user_two = UserFactory.create(username="OlaTest")
        UserFactory.create()

        # give points
        ## user one -> 320
        UserScoresFactory.create(
            profile=user_one.profile,
            points=320,
            description=UserScores.render_description(320, "WIN BET"),
        )
        UserScoresFactory.create(
            profile=user_one.profile,
            description=UserScores.render_description(10, "WIN BET"),
        )
        UserScoresFactory.create(
            profile=user_one.profile,
            points=-10,
            description=UserScores.render_description(-10, "LOSE BET"),
        )

        ## user two -> 400
        UserScoresFactory.create(
            profile=user_two.profile,
            points=400,
            description=UserScores.render_description(400, "WIN BET"),
        )

    def test_should_create_four_objects(self):
        self.assertEquals(UserScores.objects.count(), 4)

    @parameterized.expand(
        [
            (1, 320, "WIN BET"),
            (2, 10, "WIN BET"),
            (3, -10, "LOSE BET"),
            (4, 400, "WIN BET"),
        ]
    )
    def test_should_create_appropriate_description(self, pk, pt, info):
        user_scores = UserScores.objects.get(id=pk)

        self.assertEquals(user_scores.description, f"{pt} pt for: {info}.")
