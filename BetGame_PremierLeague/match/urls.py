from django.urls import path

from .views import MatchDetailView

urlpatterns = [path("<int:pk>/", MatchDetailView.as_view(), name="match-detail")]
