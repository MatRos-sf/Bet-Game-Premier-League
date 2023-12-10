from django.test import tag
from parameterized import parameterized

from league.tests.test_models import SimpleDB
from .factories.models_factory import EventFactory
from users.factories import UserFactory
from event.models import Event


@tag("event")
class EventTest(SimpleDB):
    def setUp(self):
        self.event = Event.objects.first()

    def test_should_create_one_event(self):
        self.assertEquals(Event.objects.count(), 1)

    def test_calculate_first_place_points_should_return_five_when_user_has_first_place(
        self,
    ):
        self.assertEquals(self.event.calculate_first_place_points, 5)

    def test_calculate_second_place_points_should_return_two_when_user_has_second_place(
        self,
    ):
        self.assertEquals(self.event.calculate_second_place_points, 2)

    def test_calculate_third_place_points_should_return_one_when_user_has_third_place(
        self,
    ):
        self.assertEquals(self.event.calculate_third_place_points, 1)

    @parameterized.expand(
        [(70, 30, 10), (60, 35, 100), (1, 1, 1), (95, 3, 1), (100, 1, 0)]
    )
    def test_should_create_default_aware_when_sum_aware_is_greater_than_one_hundred_or_lower(
        self, first_place, second_place, third_place
    ):
        new_event = EventFactory(
            owner=UserFactory(),
            first_place=first_place,
            second_place=second_place,
            third_place=third_place,
        )

        expected = (60, 30, 10)
        currently_result = (
            new_event.first_place,
            new_event.second_place,
            new_event.third_place,
        )
        self.assertEquals(currently_result, expected)

    @parameterized.expand(
        [(70, 20, 10), (60, 40, 0), (100, 0, 0), (95, 3, 2), (80, 0, 20)]
    )
    def test_should_create_new_aware_when_sum_aware_is_correct(
        self, first_place, second_place, third_place
    ):
        new_event = EventFactory(
            owner=UserFactory(),
            first_place=first_place,
            second_place=second_place,
            third_place=third_place,
        )

        expected = (first_place, second_place, third_place)
        currently_result = (
            new_event.first_place,
            new_event.second_place,
            new_event.third_place,
        )
        self.assertEquals(currently_result, expected)
