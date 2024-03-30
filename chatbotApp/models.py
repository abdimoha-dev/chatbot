from enum import unique
from django.db import models
# from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, AbstractUser
)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_admin = models.BooleanField(default=False) # a superuser
    username = models.CharField(max_length=254, null=False, unique=True)
    first_name = models.CharField(max_length=254, null=False, unique=False)
    last_name = models.CharField(max_length=254, null=False, unique=False)
    password = models.CharField(max_length=254, null=False)

    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [] # Email & Password are required by default.