from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField)

from users.serializers import UserSerializerCustom
from .models import Cart, Favorite, Ingredient, IngredientInRecipe, Recipe, Tag


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
        fields = (
            'name',
            'color_hex',
            'slug'
        )


class FavoriteSerializer(ModelSerializer):
    """
    Сериализатор любимых рецептов
    """
    class Meta:
        fields = ('user', 'recipe')
        model = Favorite


class RecipeSerializer(ModelSerializer):
    """
    Сериализатор рецептов
    """
    author = UserSerializerCustom(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        required=True,
        many=True
    )
    tags = PrimaryKeyRelatedField(
        many=True,
        read_only=False,
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()
    is_favorite = SerializerMethodField('check_is_favorite')
    is_in_cart = SerializerMethodField('check_is_in_cart')

    @staticmethod
    def create_recipe_ingredients(recipe, ingredients):

        for ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )

    def create(self, data):

        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        recipe = Recipe.objects.create(**data)
        recipe.tags.set(tags)
        self.create_recipe_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, data):

        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_recipe_ingredients(instance, ingredients)
        instance.tags.set(tags)

        return super().update(instance, data)

    def check_is_favorite(self, obj):

        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False

        is_favorite = Favorite.objects.filter(
            recipe=obj,
            user=current_user
        ).exists()

        return is_favorite

    def check_is_in_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False

        is_in_cart = Cart.objects.filter(
            recipe=obj,
            user=current_user
        ).exists()

        return is_in_cart

    class Meta:
        model = Recipe
        fields = ('name',
                  'is_favorite',
                  'author',
                  'ingredients',
                  'tags',
                  'text',
                  'pub_date',
                  'cooking_time',
                  'is_in_cart',
                  'image'
        )
