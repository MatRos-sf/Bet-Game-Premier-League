from django.test import TestCase
from django.contrib.auth.models import User
from django.test import tag
from users.models import Profile
from ..factories.user import UserFactory


@tag("users_tag")
class UserSignalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserFactory()
        UserFactory()
        UserFactory()

    def setUp(self):
        self.profile_one = User.objects.get(id=1)
        self.profile_two = User.objects.get(id=2)
        self.profile_three = User.objects.get(id=3)

    def test_should_create_three_profile(self):
        self.assertEquals(Profile.objects.count(), 3)
