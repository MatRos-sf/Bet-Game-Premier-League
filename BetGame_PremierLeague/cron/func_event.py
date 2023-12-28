from django.contrib.auth.models import User
from django.utils import timezone
from notifications.signals import notify

from users.models import UserScores
from event.models import Event, EventRequest


def provide_user_points(user: User, points: int, place: str, event: Event) -> None:
    if points > 0:
        description = UserScores.render_description(
            points, f"event {event.pk} {place} place"
        )
        UserScores.objects.create(
            profile=user.profile,
            points=points,
            description=description,
            kind=UserScores.Kind.EVENT,
        )
        notify.send(
            event,
            recipient=user,
            verb=f"has finished; you earned {points} pt. for the {place} place.",
        )
    else:
        notify.send(
            event, recipient=user, verb=f"has finished. You are in the {place} place."
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
    events = Event.objects.filter(end_date__lt=timezone.now(), status=Event.NOW)

    if events.exists():
        for event in events:
            rank = event.rank[:3]  # place_1, place_2, place_3 = event.rank[:3]
            number_of_members = event.amt_members

            if number_of_members > 0:
                first_place_points = event.calculate_first_place_points
                provide_user_points(rank[0], first_place_points, "1st", event)

            if number_of_members > 1:
                second_place_points = event.calculate_second_place_points
                provide_user_points(
                    rank[1], second_place_points, f"event {event.pk} 2nd place", event
                )

            if number_of_members > 2:
                third_place_points = event.calculate_third_place_points
                provide_user_points(
                    rank[2], third_place_points, f"event {event.pk} 3rd place", event
                )

            # send notification others members about finished event
            other_members = set(event.members.all()).difference(set(rank))
            for user in other_members:
                notify.send(event, recipient=user, verb="has finished.")
        events.update(status="finished")


def check_event() -> str:
    start_event()
    finish_event()

    return "Events have been updated!"
