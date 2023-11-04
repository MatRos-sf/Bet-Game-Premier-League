from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, ProfileDetailView, ProfileListView, home, edit_profile


urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="user-register"),
    path(
        "login/", LoginView.as_view(template_name="users/login.html"), name="user-login"
    ),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logout.html"),
        name="user-logout",
    ),
    path("profiles/", ProfileListView.as_view(), name="user-profile-list"),
    path(
        "profile/<str:slag>/", ProfileDetailView.as_view(), name="user-profile-detail"
    ),
    path("profile/<str:username>/edit/", edit_profile, name="user-profile-edit"),
]
