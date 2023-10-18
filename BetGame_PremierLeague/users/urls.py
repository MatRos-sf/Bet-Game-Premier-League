from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, ProfileDetailView


urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/<str:slag>/', ProfileDetailView.as_view(), name='profile-detail')
]