from django.urls import path, include

from .views import create

urlpatterns = [path("create/", create)]
