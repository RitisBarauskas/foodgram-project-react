from rest_framework.serializers import ModelSerializer

from .models import Tag, Ingredient


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор ингердиентов
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """
    Сериализатор тегов
    """

    class Meta:
        model = Tag
        fields = '__all__'



