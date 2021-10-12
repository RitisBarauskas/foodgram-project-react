from django_filters import rest_framework as my_filters

from .models import Ingredient, Recipe, Tag


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
    author = my_filters.NumberFilter(
        field_name='author__id',
        lookup_expr='exact'
    )
    tags = my_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = my_filters.BooleanFilter(
        field_name='is_favorited'
    )
    is_in_shopping_cart = my_filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return Recipe.objects.all()

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
