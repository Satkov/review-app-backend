from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserConfirmation
from .utils import UsernamePostfixGenerator, GetRequestFromContext, ConfirmCodeGenerator, SendVerificationCode, \
    IsConfirmationCodeIsCorrect, DoesFieldInValidatedData

User = get_user_model()


class UserConfirmationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = UserConfirmation

    def create(self, validated_data):
        code = ConfirmCodeGenerator(6)
        confirmation_record = UserConfirmation.objects.create(
            email=validated_data.get('email'),
            confirmation_code=code
        )
        SendVerificationCode(validated_data.get("email"), code)
        return confirmation_record


class UserJWTSerializer(serializers.ModelSerializer):
    """
    Проверяет верность кода подтверждения почты,
    создает аккаунт, возвращает токены
    """

    class Meta:
        fields = ('username', 'password', 'email',
                  'first_name', 'last_name')
        model = User

    def validate(self, data):
        email = data.get('email')
        confirmation_code = GetRequestFromContext(self.context).data.get('confirmation_code')
        IsConfirmationCodeIsCorrect(email, confirmation_code, True)
        return data

    def create(self, validated_data):
        username = f'User{UsernamePostfixGenerator()}'
        user = User.objects.create_user(
            email=validated_data.get('email'),
            username=username,
            password=validated_data.get('password')
        )
        user.save()
        return user

    def to_representation(self, instance):
        user = get_object_or_404(User, email=instance)
        tokens = RefreshToken.for_user(user)
        return {'refresh_token': str(tokens),
                'access_token': str(tokens.access_token)}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_superuser')
        # extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if DoesFieldInValidatedData(validated_data, 'password'):
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
