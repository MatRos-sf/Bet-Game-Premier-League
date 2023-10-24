from django.test import TestCase
from django.contrib.auth.models import User

from users.models import Profile


class SignalTest(TestCase):
    def test_should_create_profile_when_user_is_create(self):
        User.objects.create(username="Test", password="qjgN2927fQHvs1W")  # nosec

        self.assertEquals(Profile.objects.count(), 1)

    def test_should_create_10_profile_when_is_10_users(self):
        for i in range(1, 11):
            user = User.objects.create(
                username="Test" + str(i),
                password="qjgN2927fQHvs1W",  # nosec
                email=f"test{i}@test.com",
            )
            self.assertEquals(Profile.objects.get(id=i).user, user)

        self.assertEquals(Profile.objects.count(), 10)
