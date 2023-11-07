from factory.django import DjangoModelFactory, ImageField
from factory import Faker, Sequence, SubFactory
import factory

from django.contrib.auth.models import User
from users.models import Profile, UserScores
from django.db.models import signals
from league.models import Team


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    fb_id = Sequence(lambda n: f"fb_id_{n}")
    name = Sequence(lambda n: f"Team{n}")


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user_{n}")
    password = "passwordTEST"  # nosec


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class SimpleProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = SubFactory(UserFactory)


class ProfileFactory(SimpleProfileFactory):
    image = ImageField()
    support_team = SubFactory(TeamFactory)
    description = Faker("sentence")

    @factory.post_generation
    def following(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.following.add(*extracted)


class UserScores(DjangoModelFactory):
    class Meta:
        model = UserScores

    profile = SubFactory(SimpleProfileFactory)
    points = 10
    description = "description_test"


#
# @factory.django.mute_signals(signals.pre_save, signals.post_save)
# class ProfileFactory(DjangoModelFactory):
#
#     class Meta:
#         model = Profile
#
#     user = SubFactory(UserFactory)
#     image = ImageField()
#     support_team = SubFactory(TeamFactory)
#     description = Faker('sentence')
#
#     @factory.post_generation
#     def following(self, create, extracted, **kwargs):
#         if not create or not extracted:
#             return
#         self.following.add(*extracted)
#
