from django.contrib.admin import ModelAdmin, register

from .models import Ingredient, Recipe, Tag


@register(Tag)
class TagAdmin(ModelAdmin):

    """Регистрация в админке тегов рецептов"""

    list_display = ('name', 'color_hex', 'slug')
    empty_value_display = '-пусто-'
    ordering = ('color_hex',)


@register(Ingredient)
class IngredientAdmin(ModelAdmin):

    """Регистрация в админке ингредиентов"""

    list_display = ('name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    ordering = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):

    """
    Регистрация в админке модели рецептов
    """

    list_display = ('name', 'author', 'cooking_time', 'pub_date')
    list_filter = ('name', 'author', 'cooking_time', 'pub_date')
    ordering = ('-pub_date',)
    empty_value_display = '-пусто-'
