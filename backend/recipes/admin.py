from django.contrib.admin import ModelAdmin, register

from .models import Ingredient, Tag


@register(Tag)
class TagAdmin(ModelAdmin):

    """Регистрация в админке тегов рецептов"""

    list_display = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'
    ordering = ('color',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):

    """Регистрация в админке ингредиентов"""

    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    ordering = ('name',)
