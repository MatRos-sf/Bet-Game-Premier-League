from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import (
    register,
    ProfileDetailView,
    ProfileListView,
    home,
    edit_profile,
    AllUserNotificationsList,
)


urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(template_name="users/form.html"), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "profile/notifications/",
        AllUserNotificationsList.as_view(),
        name="profile-notifications",
    ),
    path("profiles/", ProfileListView.as_view(), name="profile-list"),
    path("profile/<str:slag>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profile/<str:username>/edit/", edit_profile, name="profile-edit"),
]
