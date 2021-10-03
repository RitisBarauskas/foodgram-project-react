from rest_framework.serializers import ModelSerializer

from .models import Tag, Ingredient, IngredientInRecipe, Favorite


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор ингердиентов
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(ModelSerializer):
    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """
    Сериализатор тегов
    """

    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(ModelSerializer):
    class Meta:
        fields = ('user', 'recipe')
        model = Favorite


