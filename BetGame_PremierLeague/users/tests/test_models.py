from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
from typing import Tuple
import os
import string
from django.conf import settings
from random import randint, choices

from users.models import Profile


def get_random_name(suffix: str) -> str:

    letters = string.ascii_letters + string.digits
    name = ''.join(choices(letters, k=randint(5,10)))

    return name + suffix


def get_temporary_image(size: Tuple[int, int], name: str) -> InMemoryUploadedFile:
    name = name if name.endswith('.jpg') else name + '.jpg'
    io = BytesIO()
    color = (255, 0, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(io, format='JPEG')
    image_file = InMemoryUploadedFile(io, None, name, 'jpeg', io.tell(), None)
    image_file.seek(0)

    return image_file


class ProfileTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="test", password='qjgN2927fQHvs1W')

    def setUp(self) -> None:
        self.profile = Profile.objects.get(id=1)

    def test_user_field_is_one_to_one_with_user(self):
        user = User.objects.get(id=1)
        self.assertEquals(user, self.profile.user)

    def test_image_label(self):
        field_label = self.profile._meta.get_field('image').verbose_name
        self.assertEquals(field_label, "profile picture")

    def test_should_set_default_image_when_profile_is_create(self):
        expected = '/media/default.jpg'

        self.assertEquals(self.profile.image.url, expected)

    def test_should_set_new_size_image_when_image_is_too_high(self):

        name = get_random_name('.jpg')
        self.profile.image = get_temporary_image((301,19), name)
        self.profile.save()

        self.assertEquals(self.profile.image.name, "profile_pics/" + name)
        os.remove(os.path.join(settings.BASE_DIR, "media", "profile_pics", name))

    def test_str_method_should_return_username(self):
        expected_obj_name = f"{self.profile.user}"
        self.assertEquals(str(self.profile), expected_obj_name)

    def test_get_absolute_url(self):
        expected = '/profile/test/'
        self.assertEquals(self.profile.get_absolute_url(), expected)
