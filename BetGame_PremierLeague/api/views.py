from django.contrib.auth.models import User
from .serializers import UserSerializer, ProfileSerializer, BetSerializer
from rest_framework import generics

from users.models import Profile
from bet.models import Bet


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    lookup_field = "user__username"


class BetView(generics.ListAPIView):
    serializer_class = BetSerializer
    lookup_field = "user__username"

    def get_queryset(self):
        username = self.kwargs.get(self.lookup_field)
        return Bet.objects.filter(user__username=username).select_related(
            "user", "match", "match__home_team", "match__away_team"
        )
