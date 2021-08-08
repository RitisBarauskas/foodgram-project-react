from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Создаем абстрактную модель пользователя, переопределив email (уникальный) и username (короче)
    """
    email = models.EmailField(
        unique=True,
        blank=False,
        verbose_name='Email пользователя'
    )
    username = models.CharField(
        unique=True,
        blank=False,
        max_length=30,
        verbose_name='Юзернейм пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('username',)

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='uniq_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
