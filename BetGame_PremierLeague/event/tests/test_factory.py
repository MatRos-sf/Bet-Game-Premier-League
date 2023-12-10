from django.test import TestCase, tag
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from .factories.models_factory import EventFactory, EventRequestFactory
from users.factories import UserFactory
from event.models import Event, EventRequest


@tag("event_factory")
class EventFactoryTest(TestCase):
    def setUp(self):
        some_day = timezone.now() + timedelta(days=2)
        EventFactory(start_date=some_day, end_date=some_day + timedelta(days=23))

    def test_should_create_model(self):
        self.assertEquals(User.objects.count(), 1)
        self.assertEquals(Event.objects.count(), 1)

    def test_should_add_owner_to_members(self):
        event = Event.objects.first()
        self.assertIn(event.owner, event.members.all())

    def test_should_add_more_members(self):
        event = Event.objects.first()

        user_one, user_two = UserFactory.create_batch(2)
        event.members.add(user_one, user_two)

        self.assertEquals(event.members.count(), 3)


@tag("event_request_factory")
class EventRequestFactoryTest(TestCase):
    def setUp(self):
        some_day = timezone.now() + timedelta(days=2)
        self.user_one, self.user_two, self.user_three = UserFactory.create_batch(3)
        self.event = EventFactory(
            owner=self.user_one,
            start_date=some_day,
            end_date=some_day + timedelta(days=23),
        )
        EventRequestFactory(
            sender=self.user_one, receiver=self.user_two, event=self.event
        )

    def test_should_create_model(self):
        self.assertEquals(Event.objects.count(), 1)
        self.assertEquals(EventRequest.objects.count(), 1)

    def test_should_add_new_request(self):
        EventRequestFactory(
            sender=self.user_one, receiver=self.user_three, event=self.event
        )
        self.assertEquals(EventRequest.objects.count(), 2)
