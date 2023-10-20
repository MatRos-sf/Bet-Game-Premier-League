from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.LeagueListView.as_view(), name='league-list'),
    path('<int:pk>/', views.LeagueDetailView.as_view(), name='league-detail'),
    path('<int:pk>/update/', views.LeagueUpdateView.as_view(), name='league-update')
]
