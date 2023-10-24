from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import File
from django.conf import settings
from django.test import tag
from parameterized import parameterized, parameterized_class

from PIL import Image
from io import BytesIO
from typing import Tuple
import os
import string
from random import randint, choices

from users.models import Profile


def get_random_name(suffix: str) -> str:
    letters = string.ascii_letters + string.digits
    name = "".join(choices(letters, k=randint(5, 10)))

    return name + suffix


def get_temporary_image(size: Tuple[int, int], name: str) -> File:
    name = name if name.endswith(".jpg") else name + ".jpg"
    file_obj = BytesIO()
    color = (256, 0, 0)
    image = Image.new("RGB", size=size, color=color)
    image.save(file_obj, format="JPEG")

    file_obj.seek(0)

    return File(file_obj, name=name)


@tag("profile")
class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="test", password="qjgN2927fQHvs1W")  # nosec

    def setUp(self) -> None:
        self.profile = Profile.objects.get(id=1)

    def test_user_field_is_one_to_one_with_user(self):
        user = User.objects.get(id=1)
        self.assertEquals(user, self.profile.user)

    def test_image_label(self):
        field_label = self.profile._meta.get_field("image").verbose_name
        self.assertEquals(field_label, "profile picture")

    def test_should_set_default_image_when_profile_is_create(self):
        expected = "/media/default.jpg"

        self.assertEquals(self.profile.image.url, expected)

    @parameterized.expand([(30, 301, 300), (250, 312, 300), (250, 550, 300)])
    def test_should_set_new_default_height_image_when_image_is_too_height(
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

    def test_str_method_should_return_username(self):
        expected_obj_name = f"{self.profile.user}"
        self.assertEquals(str(self.profile), expected_obj_name)

    def test_get_absolute_url(self):
        expected = "/profile/test/"
        self.assertEquals(self.profile.get_absolute_url(), expected)
