from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers

from .views import UserViewSet, ProfileList

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

app_name = "api"
urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('user/', UserAPIView.as_view(), name='user')
    path("list/", ProfileList.as_view())
]

urlpatterns += router.urls
