from django.test import TestCase, tag
from django.utils import timezone
from datetime import timedelta
from parameterized import parameterized
from django.core.exceptions import ValidationError


from event.forms import EventForm
from users.factories import UserFactory


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

    @parameterized.expand([0, 1, 2, 3, 4, 5])
    def test_should_expectation_when_start_date_is_before_today(self, back_day):
        start_date = timezone.now() - timedelta(days=back_day)
        payload = self.__create_payload(
            start_date=start_date, end_date=start_date + timedelta(days=back_day)
        )

        event_form = EventForm(data=payload)
        self.assertFormError(
            event_form, "start_date", "The start date of the event must be after today."
        )

    @parameterized.expand([1, 2, 3, 4, 5])
    def test_should_form_error_when_start_date_is_after_end_date(self, back_day):
        test_data = timezone.now() + timedelta(weeks=2)
        end_date = test_data - timedelta(days=back_day)
        payload = self.__create_payload(start_date=test_data, end_date=end_date)

        event_form = EventForm(data=payload)
        self.assertFalse(event_form.is_valid())
        self.assertIsInstance(
            event_form.errors.as_data()["__all__"][0], ValidationError
        )
        self.assertEquals(
            event_form.errors.as_data()["__all__"][0].message,
            "Start Date cannot be great than End Date",
        )

    def test_should_form_error_when_start_date_is_the_same_end_date(self):
        test_data = timezone.now() + timedelta(weeks=2)
        payload = self.__create_payload(start_date=test_data, end_date=test_data)

        event_form = EventForm(data=payload)
        self.assertFalse(event_form.is_valid())
        self.assertIsInstance(
            event_form.errors.as_data()["__all__"][0], ValidationError
        )
        self.assertEquals(
            event_form.errors.as_data()["__all__"][0].message,
            "The dates must be different.",
        )
