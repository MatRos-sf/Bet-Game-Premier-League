from django.contrib.auth.models import User

from rest_framework import serializers

from users.models import Profile


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y/%m/%d")

    class Meta:
        model = User
        fields = ["pk", "username", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    points = serializers.IntegerField(source="all_points")
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["description", "url", "points", "user"]
