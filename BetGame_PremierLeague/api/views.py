from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, ProfileSerializer, BetSerializer
from users.models import Profile
from bet.models import Bet


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = User.objects.all()
        serializer = UserSerializer(data, many=True)
        response = {"count": data.count(), "users": serializer.data}
        return Response(response, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveAPIView):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    lookup_field = "user__username"
    permission_classes = [IsAuthenticated]


class BetView(generics.ListAPIView):
    serializer_class = BetSerializer
    lookup_field = "user__username"
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs.get(self.lookup_field)
        return Bet.objects.filter(user__username=username).select_related(
            "user", "match", "match__home_team", "match__away_team"
        )

    def get(self, request, *args, **kwargs):
        data = self.get_queryset()
        serializer = BetSerializer(data, many=True)
        response = {"count": data.count(), "bets": serializer.data}
        return Response(response, status=status.HTTP_200_OK)
