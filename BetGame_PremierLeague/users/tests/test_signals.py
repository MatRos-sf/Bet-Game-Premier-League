from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile
from ..factories.user import UserFactory


class UserSignalTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(UserSignalTest, cls).setUpClass()
        UserFactory()
        UserFactory()
        UserFactory()

    def test_should_create_three_profile(self):
        self.assertEquals(Profile.objects.count(), 3)
