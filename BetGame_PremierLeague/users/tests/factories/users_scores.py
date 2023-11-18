from factory.django import DjangoModelFactory
from factory import SubFactory

from .profile import SimpleProfileFactory
from users.models import UserScores


class UserScoresFactory(DjangoModelFactory):
    class Meta:
        model = UserScores

    profile = SubFactory(SimpleProfileFactory)
    points = 10
    description = "description_test"
