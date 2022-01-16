from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserConfirmation
from .utils import UsernamePostfixGenerator, GetRequestFromContext, ConfirmCodeGenerator, SendVerificationCode

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
    class Meta:
        fields = ('username', 'password', 'email',
                  'first_name', 'last_name')
        model = User

    def validate(self, data):
        email = data.get('email')
        confirmation_code = GetRequestFromContext(self.context).data.get('confirmation_code')
        user_conf = UserConfirmation.objects.filter(
            email=email, confirmation_code=confirmation_code).first()
        if user_conf is None:
            raise ValidationError(
                'Confirmation code is not correct')
        user_conf.delete()
        return data

    def create(self, validated_data):
        username = f'User{UsernamePostfixGenerator()}'
        user = User.objects.create(
            email=validated_data.get('email'),
            username=username
        )
        user.set_password(validated_data.get('password'))
        return user

    def to_representation(self, instance):
        user = get_object_or_404(User, email=instance)
        refresh = RefreshToken.for_user(user)
        data = {'token': str(refresh.access_token)}
        return data


class UsersViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('username', 'password', 'email',
                  'first_name', 'last_name', 'is_superuser')
        model = User
