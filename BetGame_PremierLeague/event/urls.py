from django.urls import path, include

from .views import (
    create,
    EventDetailView,
    RequestListViews,
    answer_to_request,
    EventListView,
)

app_name = "event"

urlpatterns = [
    path("", EventListView.as_view(), name="list"),
    path("create/", create, name="create"),
    path("detail/<int:pk>/", EventDetailView.as_view(), name="detail"),
    path("requests/", RequestListViews.as_view(), name="requests"),
    path("requests/<int:pk>/answer/", answer_to_request, name="answer_to_request"),
]
