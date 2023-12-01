from django.contrib.auth.models import User
from django.utils import timezone

from users.models import UserScores
from event.models import Event, EventRequest


def provide_user_points(user: User, points: int, info: str) -> None:
    if points > 0:
        description = UserScores.render_description(points, info)
        UserScores.objects.create(
            profile=user.profile, points=points, description=description
        )


def start_event() -> None:
    """
    Search for events, change their status to 'now,' and cancel all requests because the time has expired.
    """
    Event.objects.filter(start_date__lte=timezone.now(), status=Event.BEFORE).update(
        status=Event.NOW
    )

    EventRequest.objects.filter(
        event__status=Event.NOW, is_accept=False, canceled=False
    ).update(canceled=True)


def finish_event() -> None:
    """
    Search for the event to finish and give away prizes.
    """
    events = Event.objects.filter(end_date__gt=timezone.now(), status=Event.NOW)

    events.update(status="finished")

    if events.exists():
        for event in events:
            if event.fee == 0:
                continue

            rank = event.rank[:3]  # place_1, place_2, place_3 = event.rank[:3]
            number_of_members = event.amt_members

            if number_of_members > 0:
                first_place_points = event.calculate_first_place_points
                provide_user_points(
                    rank[0], first_place_points, f"event {event.pk} 1st place"
                )

            if number_of_members > 1:
                second_place_points = event.calculate_second_place_points
                provide_user_points(
                    rank[1], second_place_points, f"event {event.pk} 2nd place"
                )

            if number_of_members > 2:
                third_place_points = event.calculate_third_place_points
                provide_user_points(
                    rank[2], third_place_points, f"event {event.pk} 3rd place"
                )


def check_event() -> str:
    start_event()
    finish_event()

    return "Events have been updated!"
