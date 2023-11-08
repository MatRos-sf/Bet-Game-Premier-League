from factory.django import DjangoModelFactory
from factory import Sequence

from django.contrib.auth.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user_{n}")
    password = "passwordTEST"  # nosec
