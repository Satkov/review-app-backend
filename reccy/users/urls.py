from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import EmailConfirmationViewSet, CreateNewUserSendJWTViewSet, UsersViewSet, RefreshJWTAPIView

v1_router = DefaultRouter()

v1_router.register(
    r'users',
    UsersViewSet,
    basename='username'
)

v1_router.register(
    r'auth/token/email_confirmation',
    CreateNewUserSendJWTViewSet,
)

v1_router.register(
    r'auth/email',
    EmailConfirmationViewSet,
)


urlpatterns = [
    path('v1/auth/token/password/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/auth/forgot_password/', RefreshJWTAPIView.as_view(), name='refresh_token'),
    path('v1/', include(v1_router.urls)),
]