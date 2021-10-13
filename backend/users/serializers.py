from django.contrib.auth import authenticate, get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe

from .models import Follow

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    """
    Сериалзиатор регистрации пользователей (используется в сеттингс)
    """
    class Meta(UserCreateSerializer.Meta):
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializerCustom(UserSerializer):
    """
    Кастомный пользовательский сериализатор
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class AuthTokenSerializer(serializers.Serializer):
    """
    Сериализатор аутентификации
    """
    email = serializers.EmailField(label='Email')
    password = serializers.CharField(
        label=('Password',),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attributes):
        email = attributes.get('email')
        password = attributes.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                message = 'Неверные учетные данные.'
                raise serializers.ValidationError(
                    message,
                    code='authorization',
                )
        else:
            message = 'Запрос должен содержать email и пароль.'
            raise serializers.ValidationError(message, code='authorization')

        attributes['user'] = user
        return attributes


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Мини-сериализатор рецептов
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


# class FollowUsersSerializer(serializers.ModelSerializer):
#     """
#     Сериализатор подписок (можно подписаться и отписаться)
#     """
#     id = serializers.ReadOnlyField(source='author.id')
#     email = serializers.ReadOnlyField(source='author.email')
#     username = serializers.ReadOnlyField(source='author.username')
#     first_name = serializers.ReadOnlyField(source='author.first_name')
#     last_name = serializers.ReadOnlyField(source='author.last_name')
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = RecipeShortSerializer(many=True, read_only=True)
#     recipes_count = serializers.SerializerMethodField()
#
#     def get_recipes_count(self, obj):
#         return Recipe.objects.filter(author=obj.author).count()
#
#     def get_is_subscribed(self, obj):
#         return Follow.objects.filter(
#             user=obj.user, author=obj.author
#         ).exists()
#
#     class Meta:
#         model = Follow
#         fields = (
#             'email',
#             'id',
#             'username',
#             'first_name',
#             'last_name',
#             'is_subscribed',
#             'recipes',
#             'recipes_count',
#         )


class SubscribersSerializer(serializers.ModelSerializer):
    """
    Сериализатор листа подписчиков
    """
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=request.user).exists()
