from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    username = models.CharField(
        db_index=True,
        max_length=220,
        unique=True,
        verbose_name='Уникальное имя')

    email = models.EmailField(
        db_index=True,
        unique=True,
        max_length=254,
        verbose_name='Электронная почта')

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя')

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username
    


