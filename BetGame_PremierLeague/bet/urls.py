from django.urls import path, include

from .views import BetsListView

urlpatterns = [path("", BetsListView.as_view(), name="bet-home")]
