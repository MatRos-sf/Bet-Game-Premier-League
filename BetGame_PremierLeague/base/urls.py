from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .env import env

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("league/", include("league.urls")),
    path("bet/", include("bet.urls")),
    path("match/", include("match.urls")),
    path("event/", include("event.urls")),
    path("api/", include("api.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),
    # path("silk/", include("silk.urls", namespace="silk")),
]


if env("DEBUG"):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
