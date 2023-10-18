from django.test import TestCase
from django.contrib.auth.models import User
from PIL import Image

from users.models import Profile

class ProfileTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="test", password='qjgN2927fQHvs1W')

    def test_user_field_is_one_to_one_with_user(self):
        user = User.objects.get(id=1)
        profile = Profile.objects.get(id=1)
        self.assertEquals(user, profile.user)

    def test_image_label(self):
        profile = Profile.objects.get(id=1)
        field_label = profile._meta.get_field('image').verbose_name
        self.assertEquals(field_label, "profile picture")

    def test_should_set_default_image_when_profile_is_create(self):
        profile = Profile.objects.get(id=1)
        expected = '/media/default.jpg'

        self.assertEquals(profile.image.url, expected)

    def test_should_set_new_size_image_when_image_is_too_high(self):
        pass