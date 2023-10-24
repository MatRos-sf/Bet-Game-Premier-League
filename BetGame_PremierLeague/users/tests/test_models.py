from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile, SimpleUploadedFile
from PIL import Image
from io import BytesIO, StringIO
from typing import Tuple
import os
import string
from django.conf import settings
from random import randint, choices

from users.models import Profile
from django.test import tag
from parameterized import parameterized, parameterized_class
from django.core.files.base import File


def get_random_name(suffix: str) -> str:
    letters = string.ascii_letters + string.digits
    name = "".join(choices(letters, k=randint(5, 10)))

    return name + suffix


# def get_temporary_image(size: Tuple[int, int], name: str) -> InMemoryUploadedFile:
#     name = name if name.endswith('.jpg') else name + '.jpg'
#     io = BytesIO()
#     color = (255, 0, 0, 0)
#     image = Image.new("RGB", size, color)
#     image.save(io, format='JPEG')
#     image_file = InMemoryUploadedFile(io, None, name, 'jpeg', io.tell(), None)
#     image_file.seek(0)
#
#     return image_file


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

    def test_str_method_should_return_username(self):
        expected_obj_name = f"{self.profile.user}"
        self.assertEquals(str(self.profile), expected_obj_name)

    def test_get_absolute_url(self):
        expected = "/profile/test/"
        self.assertEquals(self.profile.get_absolute_url(), expected)
