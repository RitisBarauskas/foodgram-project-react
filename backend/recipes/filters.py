from django_filters import rest_framework as my_filters

from .models import Ingredient, Recipe


class IngredientFilter(my_filters.FilterSet):
    """
    Фильтр ингредиентов.
    положение буквы или слова в названии не имеет значения
    """

    name = my_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(my_filters.FilterSet):
    """
    Фильтр рецептов
    """
    tags = my_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = my_filters.BooleanFilter(
        method='get_is_favorited',
    )
    is_in_shopping_cart = my_filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shopping_cart__user=self.request.user)
        return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'tags', 'is_in_shopping_cart')
