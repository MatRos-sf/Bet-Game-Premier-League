from django.urls import path, include
from rest_framework.authtoken import views

from .views import UserListView, ProfileView, BetView


app_name = "api"
urlpatterns = [
    path("api-token-auth/", views.obtain_auth_token),
    path("users/", UserListView.as_view(), name="users"),
    path("profile/<str:user__username>/", ProfileView.as_view(), name="profile"),
    path("bet/<str:user__username>/", BetView.as_view(), name="bet"),
]
