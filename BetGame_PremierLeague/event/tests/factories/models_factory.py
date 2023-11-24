from factory.django import DjangoModelFactory
from factory import Sequence, Faker, SubFactory
import factory
from django.utils import timezone

from event.models import Event, EventRequest
from users.tests.factories.user import UserFactory


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    owner = SubFactory(UserFactory)
    start_date = Faker("date_time", tzinfo=timezone.utc)
    end_date = Faker("date_time", tzinfo=timezone.utc)

    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.members.add(*extracted)


class EventRequestFactory(DjangoModelFactory):
    class Meta:
        model = EventRequest

    sender = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)
    event = SubFactory(EventFactory)
