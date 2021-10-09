from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Создаем абстрактную модель пользователя,
    переопределив email (уникальный) и username (короче)
    """
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email пользователя'
    )
    username = models.CharField(
        unique=True,
        blank=False,
        null=False,
        max_length=30,
        verbose_name='Юзернейм пользователя'
    )
    first_name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="Имя пользователя"
    )
    last_name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name="Фамилия пользователя"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.get_full_name()


class Follow(models.Model):

    """
    Модель подписок поользователей на других пользователей
    """

    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
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
