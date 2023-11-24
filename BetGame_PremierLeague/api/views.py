from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ProfileSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics

from users.models import Profile


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer


class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ('id', 'username')
#
#
# class UserAPIView(RetrieveAPIView):
#     permission_classes = (IsAuthenticated, )
#     serializer_class = UserSerializer
#
#     def get_object(self):
#         return self.request.user
