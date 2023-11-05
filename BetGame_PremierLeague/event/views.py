from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from .models import Event
from .forms import EventForm


@login_required
def create(request):
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cd["owner"] = request.user
            Event.objects.create(**cd)

        return redirect("home")

    return render(request, "event/event_form.html", {"form": form})
