from django.test import TestCase, tag
from django.utils import timezone
from datetime import timedelta
from parameterized import parameterized
from django.core.exceptions import ValidationError


from event.forms import EventForm
from users.tests.factories.user import UserFactory


@tag("event_form")
class EventFormTest(TestCase):
    def setUp(self):
        self.sample_user = UserFactory()

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

    @parameterized.expand([1, 2, 3, 4, 5])
    def test_should_create_event(self, back_day):
        start_date = timezone.now() + timedelta(days=back_day)
        payload = self.__create_payload(
            start_date=start_date, end_date=start_date + timedelta(days=back_day)
        )
        form = EventForm(data=payload)
        self.assertTrue(form.is_valid())

    # @parameterized.expand([0, 1, 2, 3])
    # def test_should_expectation_when_start_date_is_before_today(self, back_day):
    #     start_date = timezone.now() - timedelta(days=back_day)
    #     payload = self.__create_payload(start_date=start_date, end_date=start_date + timedelta(days=back_day))
    #
    #     event = EventForm(data=payload)
    #     self.assertTrue(event.is_valid())
