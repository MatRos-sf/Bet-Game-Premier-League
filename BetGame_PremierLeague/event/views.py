from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import QuerySet
from django.contrib import messages

from .models import Event, EventRequest
from .forms import EventForm, SearchUsernameForm


@login_required
def create(request):
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if request.user.profile.all_points - cd["fee"] < 0:
                # raise ValidationError("You don't have enough points to create event!")
                messages.warning(
                    request, "You don't have enough points to create event!"
                )
            else:
                cd["owner"] = request.user
                event = Event.objects.create(**cd)
                return redirect(event)

    return render(
        request,
        "users/form.html",
        {"form": form, "title": "Create Event", "button_name": "Create"},
    )


class EventDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Event
    template_name = "event/event_detail.html"

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        event = context["object"]
        if event.start_date > timezone.now():
            context["form"] = SearchUsernameForm()

        return context

    def post(self, request, *args, **kwargs):
        form = SearchUsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.warning(request, "User does not exists!")
                return self.get(request)

            event, created = EventRequest.objects.get_or_create(
                sender=self.request.user,
                receiver=user,
                event=self.get_object(),
            )
            if created:
                messages.success(request, f"The request for {username} has been send.")
            else:
                if event.canceled:
                    messages.warning(request, f"The user has canceled your request")
                else:
                    messages.warning(request, f"Your request has already been sent!")

        return self.get(request)

    def test_func(self):
        event = self.get_object()
        return (
            event.members.filter(id=self.request.user.id).exists()
            or event.owner == self.request.user
        )


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "event/event_list.html"

    def get_queryset(self) -> QuerySet[Event]:
        qs = self.model.objects.filter(members=self.request.user, is_finished=False)
        return qs


class RequestListViews(LoginRequiredMixin, ListView):
    model = EventRequest
    template_name = "event/request_list.html"

    def get_queryset(self) -> QuerySet[EventRequest]:
        return self.model.objects.filter(
            receiver=self.request.user, canceled=False, is_accept=False
        )


def answer_to_request(request, pk):
    if request.method == "POST":
        answer = request.POST.get("answer") in {"True"}
        rq_event = get_object_or_404(EventRequest, pk=pk, receiver=request.user)

        if answer:
            try:
                rq_event.add_to_event()
            except ValidationError as e:
                messages.info(request, e.messages[0])
        else:
            rq_event.cancel()
    return redirect("event:requests")
