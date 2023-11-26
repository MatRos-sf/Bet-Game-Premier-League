from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserListView, ProfileView, BetView


app_name = "api"
urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", UserListView.as_view(), name="users"),
    path("profile/<str:user__username>/", ProfileView.as_view(), name="profile"),
    path("bet/<str:user__username>/", BetView.as_view(), name="bet"),
]
