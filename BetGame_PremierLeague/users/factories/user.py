from factory.django import DjangoModelFactory
from factory import Sequence, PostGenerationMethodCall

from django.contrib.auth.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user_{n}")
    password = PostGenerationMethodCall("set_password", "1_test_TEST_!")
