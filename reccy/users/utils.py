import random
import math
import uuid

from django.core.mail import send_mail
from django.utils.datastructures import MultiValueDictKeyError

from reccy.settings import admin_email
from rest_framework.exceptions import ValidationError

from .models import UserConfirmation


def ConfirmCodeGenerator(length):
    digits = [i for i in range(0, 10)]
    Code = ""
    for i in range(length):
        index = math.floor(random.random() * 10)
        Code += str(digits[index])

    return Code


def UsernamePostfixGenerator():
    return str(uuid.uuid4().hex[:10])


def GetRequestFromContext(context):
    try:
        request = context.get('request')
    except KeyError:
        raise KeyError({
            'error': 'request was not received'
        })
    return request


def SendVerificationCode(email, code):
    send_mail(
        'authentication',
        f'{code}',
        admin_email,
        [email],
        fail_silently=False,
    )


def IsConfirmationCodeIsCorrect(email, code, delete):
    user_conf = UserConfirmation.objects.filter(
        email=email, confirmation_code=code).first()
    if user_conf is None:
        raise ValidationError({'errors': 'confirmation_code is required'})
    if delete:
        user_conf.delete()
    return True


def GetFieldFromRequest(request, field):
    try:
        return request.data[field]
    except MultiValueDictKeyError:
        raise ValidationError({'errors': f'{field} is required'})
