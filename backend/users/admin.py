from django.contrib.admin import ModelAdmin, register

from .models import Follow, User


@register(User)
class UserAdmin(ModelAdmin):

    """
    Модель отображения пользователей в админке
    """

    list_display = (
        'email',
        'first_name',
        'second_name',
    )
    list_filter = (
        'email',
        'username',
    )
    search_fields = (
        'email',
        'username',
    )
    empty_value_display = '-пусто-'


@register(Follow)
class FollowAdmin(ModelAdmin):

    """
    Модель отображения подписчиков в админке
    """

    list_display = ('user', 'author')
    empty_value_display = '-пусто-'
