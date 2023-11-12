import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Avg, Sum, Max, F
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from .models import Profile, UserScores
from .forms import UserRegisterForm, ProfileUpdate
from league.models import TeamStats, Season
from match.models import Match, Matchweek
from bet.models import Bet


def home(request: HttpRequest) -> HttpResponse:
    amt_of_users = User.objects.count()
    currently_season = Season.get_currently_season("Premier League")

    table = TeamStats.get_season_table(
        season=currently_season.start_date.year, league="Premier League"
    )[:8]

    last_match = Match.get_last_match()
    next_match = Match.get_next_match()

    mw = Matchweek.objects.filter(finished=True).last()
    if mw:
        last_matchweek_bet_stat = Bet.get_stats_matchweek(mw)
        last_matchweek_bet_stat["matchweek"] = mw.matchweek
    else:
        last_matchweek_bet_stat = {}

    # top 3 players
    top_players = Profile.top_players(3)

    return render(
        request,
        "users/home_page.html",
        {
            "amt_users": amt_of_users,
            "table": table,
            "last_match": last_match,
            "next_match": next_match,
            "last_bets": last_matchweek_bet_stat,
            "top_players": top_players,
        },
    )


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
    return render(
        request,
        "users/form.html",
        {"title": "Sign Up", "button_name": "Create", "form": form},
    )


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "users/profile.html"
    slug_field = "user__username"

    def get_object(self, queryset=None):
        username = self.kwargs.get("slag")

        return get_object_or_404(Profile, user__username=username)

    def get_context_data(self, **kwargs):
        username = self.kwargs.get("slag")
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        instance = context["object"]

        context["amt_following"] = instance.following.count()
        context["amt_followers"] = Profile.followers(instance.user).count()

        context["self"] = self.request.user == instance.user
        context["amt_bets"] = Bet.objects.filter(user=self.request.user).count()

        context["rank"] = Profile.position(username)

        # get info about user stats
        bet_stats = Bet.get_stats_user(User.objects.get(username=username))
        context["bet_stats"] = bet_stats

        # get last bets
        last_bets = (
            Bet.objects.filter(user__username=username)
            .exclude(is_won__isnull=True)
            .order_by("-match__start_date")[:4]
        )
        context["bets"] = last_bets

        return context


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "users/profile_list.html"

    def get_queryset(self):
        username = self.request.GET.get("username", "")
        if username:
            object_list = self.model.objects.filter(user__username__contains=username)
            if not object_list.exists():
                messages.info(self.request, f"User not found!")
        else:
            object_list = self.model.objects.none()

        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)

        # user following
        user = self.request.user
        user_profile = Profile.objects.get(user=user)
        following = user_profile.following.all()

        context["following"] = sorted(
            list(following), key=lambda x: x.profile.all_points, reverse=True
        )

        # top 10 users
        context["top_ten"] = Profile.top_players(10)

        # amount of players
        amt_of_players = self.model.objects.count()
        context["amt_players"] = amt_of_players

        return context


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        messages.warning(request, "You can only update own profile!")
        return redirect("user-profile-detail", slag=request.user.username)

    user_profile = get_object_or_404(Profile, user__username=username)
    form = ProfileUpdate(instance=user_profile)

    if request.method == "POST":
        form = ProfileUpdate(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            old_photo = Profile.objects.get(user__username=username)
            if old_photo.image.url != "/media/default.jpg":
                old_photo_path = old_photo.image.path
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            form.save()

            return redirect("user-profile-edit", username=username)

    return render(
        request,
        "users/form.html",
        {"title": "Edit Profile", "button_name": "Update", "form": form},
    )
