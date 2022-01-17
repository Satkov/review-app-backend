from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import UserFilter
from .pagination import LimitPaginator
from .utils import IsConfirmationCodeIsCorrect, GetFieldFromRequest, DeleteExistingUserConfirmationObj
from .models import UserConfirmation
from .permissions import IsCurrentUserOrAdminOrReadOnly
from .serializer import (UserConfirmationSerializer, UserJWTSerializer,
                         UserSerializer)

from django.contrib.auth import get_user_model

User = get_user_model()


class EmailConfirmationViewSet(mixins.CreateModelMixin,
                               GenericViewSet):
    """
    Получает на вход email, генерирует код подтверждения,
    удаляет UserConfirmation, если код уже запрашивался,
    сохраняет почту вместе с кодом в UserConfirmation,
    отправляет письмо с кодом подтверждения на почту
    Возвращает только статус код.
    """
    queryset = UserConfirmation.objects.all()
    serializer_class = UserConfirmationSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        DeleteExistingUserConfirmationObj(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(status=status.HTTP_201_CREATED,
                        headers=headers)


class CreateNewUserSendJWTViewSet(mixins.CreateModelMixin,
                                  GenericViewSet):
    """
    Принимает на вход почту, пароль и код подтверждения.
    Если все верно - создает аккаунт.
    Возвращает access и refresh токены.
    """
    queryset = User.objects.all()
    serializer_class = UserJWTSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class RefreshJWTAPIView(APIView):
    """
    Получает на вход почту и код подтверждения,
    если все верно - обновляет токен.
    Возвращает access и refresh токены.
    """
    permission_classes = [AllowAny, ]

    def put(self, request):
        email = GetFieldFromRequest(request, 'email')
        confirmation_code = GetFieldFromRequest(request, 'confirmation_code')
        if IsConfirmationCodeIsCorrect(email, confirmation_code, True):
            user = get_object_or_404(User, email=email)
            tokens = RefreshToken.for_user(user)
            return Response({'refresh_token': str(tokens),
                            'access_token': str(tokens.access_token)},
                            status=status.HTTP_200_OK)


class UsersViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                   mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   GenericViewSet):
    """
    ViewSet для работы с моделью User
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = LimitPaginator
    permission_classes = [IsCurrentUserOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_class = UserFilter

    @action(detail=False, methods=['GET', 'PATCH'])
    def me(self, request):
        user = self.request.user
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
