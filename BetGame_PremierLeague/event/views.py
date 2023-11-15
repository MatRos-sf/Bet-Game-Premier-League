from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import Event
from .forms import EventForm


@login_required
def create(request):
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if request.user.profile.all_points - cd["fee"] < 0:
                raise ValidationError("You don't have enough points to create event!")

            cd["owner"] = request.user
            event = Event.objects.create(**cd)

            return redirect(event)

    return render(request, "event/event_form.html", {"form": form})


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "event/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = context["object"]
        context["is_start"] = event.start_date > timezone.now()

        return context

    def post(self, request, *args, **kwargs):
        form = ...
