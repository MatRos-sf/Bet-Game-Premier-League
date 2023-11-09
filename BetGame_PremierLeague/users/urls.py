from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, ProfileDetailView, ProfileListView, home, edit_profile


urlpatterns = [
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path(
        "logout/",
        LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path("profiles/", ProfileListView.as_view(), name="profile-list"),
    path("profile/<str:slag>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profile/<str:username>/edit/", edit_profile, name="profile-edit"),
]
