from django.db.models import signals
from factory.django import DjangoModelFactory, ImageField
from factory import Faker, SubFactory, Sequence
import factory

from .user import UserFactory
from users.models import Profile, UserScores
from league.models import Team


class TeamFactory(DjangoModelFactory):
    class Meta:
        model = Team

    fb_id = Sequence(lambda n: f"fb_id_{n}")
    name = Sequence(lambda n: f"Team{n}")


@factory.django.mute_signals(signals.pre_save, signals.post_save)
class SimpleProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = SubFactory(UserFactory)


class ProfileFactory(SimpleProfileFactory):
    support_team = SubFactory(TeamFactory)
    description = Faker("sentence")

    @factory.post_generation
    def following(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.following.add(*extracted)


class ExtendProfileFactory(ProfileFactory):
    image = ImageField()
