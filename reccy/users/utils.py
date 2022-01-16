import random
import math
import uuid

from django.core.mail import send_mail

from reccy.settings import admin_email


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