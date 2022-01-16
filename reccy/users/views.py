from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import filters, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserConfirmation
from .permissions import IsCurrentUserOrAdminOrReadOnly
from .serializer import (UserConfirmationSerializer, UserJWTSerializer,
                         UsersViewSetSerializer)

from django.contrib.auth import get_user_model

from .utils import IsConfirmationCodeIsCorrect, IsFieldInRequest

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
        return Response('Check your Email',
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class SendJWTViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
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


class RefreshJWTAPIView(APIView):
    """
    Получает на вход почту и код подтверждения
    возвращает
    """
    permission_classes = [AllowAny, ]

    def put(self, request):
        email = IsFieldInRequest(request, 'email')
        confirmation_code = IsFieldInRequest(request, 'confirmation_code')
        if IsConfirmationCodeIsCorrect(email, confirmation_code, True):
            user = get_object_or_404(User, email=email)
            refresh = RefreshToken.for_user(user)
            data = {'token': str(refresh.access_token)}
            return Response(data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с моделью User
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UsersViewSetSerializer
    permission_classes = [IsCurrentUserOrAdminOrReadOnly, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ["=email"]

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
