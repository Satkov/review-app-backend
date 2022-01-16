from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import UserConfirmation
from .serializer import (UserConfirmationSerializer, UserJWTSerializer,
                         UsersViewSetSerializer)

from django.contrib.auth import get_user_model

User = get_user_model()


class EmailConfirmationViewSet(mixins.CreateModelMixin,
                               GenericViewSet):
    """
    Получает на вход email, генерирует код подтверждения,
    удаляет UserConfirmation, если код уже запрашивался,
    сохраняет почту вместе с кодом в UserConfirmation,
    отправляет письмо с кодом подтверждения на почту
    """
    queryset = UserConfirmation.objects.all()
    serializer_class = UserConfirmationSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, *args, **kwargs):
        try:
            if UserConfirmation.objects.filter(email=request.data['email']).exists():
                UserConfirmation.objects.filter(email=request.data['email']).delete()
        except MultiValueDictKeyError:
            raise ValidationError({'errors': 'Email is required'})

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response('Check your Email', status=status.HTTP_201_CREATED, headers=headers)


class SendJWTViewSet(mixins.CreateModelMixin,
                     GenericViewSet):
    """
    Принимает на вход почту, пароль и код подтверждения.
    Если все верно - создает аккаунт и возвращает токен.
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


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью User
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersViewSetSerializer
    permission_classes = [IsAdminUser, ]
    filter_backends = [filters.SearchFilter]
    search_fields = "username"
    lookup_field = "username"

    @action(detail=False, methods=['GET', 'PATCH'],
            permission_classes=[IsAuthenticated, ])
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
