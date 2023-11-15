from django.urls import path, include

from .views import create, EventDetailView

app_name = "event"

urlpatterns = [
    path("create/", create, name="create"),
    path("detail/<int:pk>/", EventDetailView.as_view(), name="detail"),
]
