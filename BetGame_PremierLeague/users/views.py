from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Profile
from .forms import UserRegisterForm
from bet.models import Bet
from django.db.models import Avg


def home(request):
    amt_of_users = User.objects.all().count()
    return render(request, "users/home_page.html", {"amt_users": amt_of_users})


def register(request):
    if request.user.is_authenticated:
        name = request.user.username
        logout(request)
        messages.info(request, f"Dear {name}, you have been successfully log out!")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"Dear {username}, you have been successfully signed up!"
            )
            return redirect("login")

    form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/profile.html"
    slug_field = "user__username"

    def get_object(self, queryset=None):
        username = self.kwargs.get("slag")

        return get_object_or_404(Profile, user__username=username)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context["amt_bets"] = Bet.objects.filter(user=self.request.user).count()
        win_rate = Bet.objects.aggregate(win_rate=Avg("is_won"))["win_rate"]
        context["win_rate"] = round(win_rate * 100, 2)

        return context


# TODO: setting: edit profile, passsword, picture,
