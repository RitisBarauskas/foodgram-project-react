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
        trim_whitespace=False,
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


class AddFollowSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписки на пользователя
    """

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'user'),
                message='Вы уже подписаны на автора',
            )
        ]


class SubscribersSerializer(serializers.ModelSerializer):
    """
    Сериализатор листа подписчиков и удаления подписки
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
