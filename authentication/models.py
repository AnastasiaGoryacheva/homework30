from django.contrib.auth.models import AbstractUser
from django.db import models

from abs.models import Location


class User(AbstractUser):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLES = [(MEMBER, "Пользователь"), (MODERATOR, "Модератор"), (ADMIN, "Администратор")]

    role = models.CharField(max_length=9, choices=ROLES, default=MEMBER)
    age = models.PositiveSmallIntegerField(null=True)
    locations = models.ManyToManyField(Location)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username
