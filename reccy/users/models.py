from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=191, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class UserConfirmation(models.Model):
    """
    Store confirmation code for phone registration
    """
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(
        max_length=1000, blank=True, null=True)
