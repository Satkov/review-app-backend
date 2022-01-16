from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmailConfirmationViewSet, SendJWTViewSet, UsersViewSet, RefreshJWTAPIView

v1_router = DefaultRouter()

v1_router.register(
    r'users',
    UsersViewSet,
    basename='username'
)

v1_router.register(
    r'auth/token',
    SendJWTViewSet,
)

v1_router.register(
    r'auth/email',
    EmailConfirmationViewSet,
)


urlpatterns = [
    path('v1/auth/refresh_token/', RefreshJWTAPIView.as_view(), name='refresh_token'),
    path('v1/', include(v1_router.urls)),
]