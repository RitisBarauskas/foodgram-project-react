from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F


class User(AbstractUser):
    """
    Создаем абстрактную модель пользователя,
    переопределив email (уникальный) и username (короче)
    """
    email = models.EmailField(
        unique=True,
        verbose_name='Email пользователя'
    )
    username = models.CharField(
        unique=True,
        max_length=30,
        verbose_name='Юзернейм пользователя'
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя пользователя"
    )
    last_name = models.CharField(
        max_length=50,
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
    Модель подписок пользователей на других пользователей
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_by',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='uniq_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='follower_and_following_can_not_be_equal',
            )
        ]
        ordering = ('author_id',)

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
