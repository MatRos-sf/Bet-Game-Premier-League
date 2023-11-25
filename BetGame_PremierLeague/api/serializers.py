from django.contrib.auth.models import User

from rest_framework import serializers

from users.models import Profile
from bet.models import Bet
from match.models import Match


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y/%m/%d")

    class Meta:
        model = User
        fields = ["pk", "username", "date_joined"]


class MatchSerializer(serializers.ModelSerializer):
    home_team = serializers.SlugRelatedField("name", read_only=True)
    away_team = serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = Match
        fields = ["home_team", "away_team", "home_goals", "away_goals"]


class BetSerializer(serializers.ModelSerializer):
    match = MatchSerializer()

    class Meta:
        model = Bet
        fields = ["match", "choice", "risk", "is_won"]


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    points = serializers.IntegerField(source="all_points")
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["description", "url", "points", "user"]
