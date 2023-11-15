from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from django.db.models import Sum, Q


class Event(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="events", blank=True)

    start_date = models.DateTimeField(help_text="Y-M-D")
    end_date = models.DateTimeField(help_text="Y-M-D")
    description = models.TextField(max_length=300, blank=True, null=True)

    fee = models.IntegerField(default=0)
    first_place = models.PositiveSmallIntegerField(
        default=60,
        help_text="The field that specifies the percentage win for 1st place.",
    )
    second_place = models.PositiveSmallIntegerField(
        default=30,
        help_text="The field that specifies the percentage win for 2nd place.",
    )
    third_place = models.PositiveSmallIntegerField(
        default=10,
        help_text="The field that specifies the percentage win for 3rd place.",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # check award
        first_place = self.first_place
        second_place = self.second_place
        third_place = self.third_place

        total = first_place + second_place + third_place

        if total != 100:
            # set default
            self.first_place = 60
            self.second_place = 30
            self.third_place = 10
            self.save()

    def get_absolute_url(self):
        return reverse("event:detail", args=[self.pk])

    @property
    def amt_members(self):
        return self.members.count()

    @property
    def rank(self):
        total_points = Sum(
            "profile__points__points",
            filter=Q(profile__points__got__gt=self.start_date)
            & Q(profile__points__got__lt=self.end_date),
            default=0,
        )

        rank = self.members.annotate(total_points=total_points).order_by(
            "-total_points"
        )
        return rank

    def info_fee(self):
        return f"The entrance fee is {self.fee} pts."


class EventRequest(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        User, related_name="got_requests", on_delete=models.CASCADE
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    description = models.TextField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    canceled = models.BooleanField(default=False)
    is_accept = models.BooleanField(default=False)
