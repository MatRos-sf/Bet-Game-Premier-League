from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse
from http import HTTPStatus
from django.utils import timezone
from datetime import timedelta
from parameterized import parameterized
from typing import Optional

from league.tests.test_models import SimpleDB
from event.models import Event, EventRequest
from event.forms import SearchUsernameForm
from .factories.models_factory import EventFactory, EventRequestFactory
from users.tests.factories.user import UserFactory


@tag("event_create_view")
class CreateTest(SimpleDB):
    def setUp(self):
        self.url = "/event/create/"
        self.url_name = "event:create"
        self.sample_user = User.objects.first()

    def __create_payload(self, **kwargs):
        payload = {
            "owner": self.sample_user.pk,
            "fee": 0,
            "first_place": 60,
            "second_place": 30,
            "third_place": 10,
        }
        for key, value in kwargs.items():
            payload[key] = value

        return payload

    def test_view_url_does_not_exist_when_user_is_not_authenticated(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_by_name_does_not_exist_when_user_is_not_authenticated(self):
        response = self.client.get(reverse(self.url_name))

        self.assertRedirects(response, f"/login/?next={self.url}")

    def test_view_url_exist_at_desired_location_when_user_is_authenticated(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_should_create_free_event(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        start_event = timezone.now() + timedelta(days=3)
        end_event = start_event + timedelta(days=7)
        amt_events_now = Event.objects.count()

        payload = self.__create_payload(start_date=start_event, end_date=end_event)

        response = self.client.post(self.url, data=payload)

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
        self.assertEquals(Event.objects.count(), amt_events_now + 1)

    @parameterized.expand([100, 200, 300])
    def test_should_not_create_event_when_is_too_expensive(self, fee):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        start_event = timezone.now() + timedelta(days=3)
        end_event = start_event + timedelta(days=7)
        amt_events_now = Event.objects.count()
        expected_message = "You don't have enough points to create event!"
        payload = self.__create_payload(
            start_date=start_event, end_date=end_event, fee=fee
        )

        response = self.client.post(self.url, data=payload)
        self.assertEquals(len(response.context["messages"]), 1)
        message = list(response.context["messages"])[0]

        self.assertEquals(Event.objects.count(), amt_events_now)
        self.assertEquals(message.tags, "warning")
        self.assertEquals(message.message, expected_message)


@tag("event_detal_view")
class EventDetailViewTest(SimpleDB):
    def setUp(self):
        self.url = lambda x: f"/event/detail/{x}/"
        self.url_name = "event:detail"
        self.sample_user = User.objects.first()

    def __login_user(self, user: Optional[str] = None):
        self.client.login(
            username=user or self.sample_user.username, password="1_test_TEST_!"
        )

    def __create_default_event(self, owner: Optional[str] = None) -> EventFactory:
        start_date_event = timezone.now() + timedelta(days=3)
        new_event = EventFactory(
            start_date=start_date_event,
            end_date=start_date_event + timedelta(days=3),
            owner=owner or self.sample_user,
        )
        return new_event

    def test_view_user_should_access_when_is_owner_or_members(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url(1))
        self.assertEquals(response.status_code, HTTPStatus.OK)

    def test_user_should_not_access_when_is_not_owner_or_members(self):
        guest = UserFactory()
        self.client.login(username=guest.username, password="1_test_TEST_!")

        response = self.client.get(self.url(1))
        self.assertEquals(response.status_code, HTTPStatus.FORBIDDEN)

    def test_should_not_add_form_when_event_has_been_started(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        response = self.client.get(self.url(1))
        self.assertFalse(response.context.get("form", False))

    def test_should_add_form_when_event_has_not_been_started_yet(self):
        start_date_event = timezone.now() + timedelta(days=3)
        new_event = EventFactory(
            start_date=start_date_event,
            end_date=start_date_event + timedelta(days=3),
            owner=self.sample_user,
        )

        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")

        response = self.client.get(self.url(new_event.pk))
        self.assertTrue(response.context["form"])

    def test_should_add_new_member_to_event(self):
        self.client.login(username=self.sample_user.username, password="1_test_TEST_!")
        start_date_event = timezone.now() + timedelta(days=3)
        new_event = EventFactory(
            start_date=start_date_event,
            end_date=start_date_event + timedelta(days=3),
            owner=self.sample_user,
        )
        new_user = UserFactory()
        amt_request = EventRequest.objects.count()
        self.client.post(self.url(new_event.pk), {"username": new_user.username})

        self.assertEquals(EventRequest.objects.count(), amt_request + 1)

    def test_should_add_new_member_to_event_with_message(self):
        self.__login_user()
        new_event = self.__create_default_event()

        new_user = UserFactory()
        expect_message = f"The request for {new_user.username} has been send."
        response = self.client.post(
            self.url(new_event.pk), {"username": new_user.username}
        )
        message = list(response.context["messages"])[0]

        self.assertEquals(message.tags, "success")
        self.assertEquals(message.message, expect_message)

    def test_should_not_add_user_when_user_does_not_exist(self):
        self.__login_user()
        new_event = self.__create_default_event()

        expect_message = f"User does not exists!"
        response = self.client.post(
            self.url(new_event.pk), {"username": "test_user_does_not_exist"}
        )

        message = list(response.context["messages"])[0]

        self.assertEquals(message.tags, "warning")
        self.assertEquals(message.message, expect_message)

    def test_should_not_send_request_when_user_canceled_it_before(self):
        self.__login_user()
        new_event = self.__create_default_event()
        new_user = UserFactory()
        old_request = EventRequestFactory(
            sender=self.sample_user, receiver=new_user, event=new_event
        )
        old_request.cancel()

        expect_message = f"The user has canceled your request"
        response = self.client.post(
            self.url(new_event.pk), {"username": new_user.username}
        )

        message = list(response.context["messages"])[0]

        self.assertEquals(message.tags, "warning")
        self.assertEquals(message.message, expect_message)

    def test_should_not_send_request_when_user_dont_accept_old_request(self):
        self.__login_user()
        new_event = self.__create_default_event()
        new_user = UserFactory()
        old_request = EventRequestFactory(
            sender=self.sample_user, receiver=new_user, event=new_event
        )

        expect_message = f"Your request has already been sent!"
        response = self.client.post(
            self.url(new_event.pk), {"username": new_user.username}
        )

        message = list(response.context["messages"])[0]

        self.assertEquals(message.tags, "warning")
        self.assertEquals(message.message, expect_message)
