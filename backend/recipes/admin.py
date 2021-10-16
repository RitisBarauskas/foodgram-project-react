from django.contrib.admin import ModelAdmin, TabularInline, register

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


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


class IngredientInRecipeInline(TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 1


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'author')
    list_filter = ['name', 'author', 'tags']
    inlines = (IngredientInRecipeInline,)


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = '-пусто-'


@register(ShoppingCart)
class ShoppingListAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    empty_value_display = '-пусто-'
