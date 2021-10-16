import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers, status

from users.serializers import UserSerializerCustom
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингердиентов
    """

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов
    """

    class Meta:
        model = Tag
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингердиентов в рецепте
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериалзиатор создания рецепт-ингридентов
    """
    recipe = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('recipe', 'id', 'amount')


class RecipeMiniSerializer(serializers.ModelSerializer):
    """
    Мини-сериалайзер рецептов
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializerCustom(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amount',
        many=True
    )

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериалзиатор отдает список рецептов
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializerCustom(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amount',
        many=True
    )
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор обновления и добавления новых рецептов
    """
    ingredients = IngredientCreateInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField()
    author = UserSerializerCustom(required=False)

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Вы забыли про ингредиенты'},
                status.HTTP_400_BAD_REQUEST,
            )
        valid_list = []
        for ingredient in ingredients:
            if ingredient in valid_list:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты должны быть уникальными'},
                    status.HTTP_400_BAD_REQUEST,
                )
            valid_list.append(ingredient)
            if int(ingredient['amount']) < 1:
                raise serializers.ValidationError(
                    {'ingredients':
                         'Количество ингердиента должно быть 1 или больше'},
                    status.HTTP_400_BAD_REQUEST,
                )
        return data

    @staticmethod
    def _create_data(ingredients, obj):
        create_ingredients = [
            IngredientInRecipe(
                recipe=obj,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]

        IngredientInRecipe.objects.bulk_create(
            create_ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._create_data(ingredients, recipe)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
        self._create_data(ingredients, instance)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeMiniSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериалзиатор добавления в избранное
    """
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже добавлен в избранное',
            )
        ]


class ShoppingCartSerializer(FavoriteSerializer):
    """
    Сериалзиатор добавления в корзину
    """
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('recipe', 'user'),
                message='Рецепт уже находится в списке покупок',
            )
        ]
