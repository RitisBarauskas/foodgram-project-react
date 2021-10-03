from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Follow

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField('user_is_subscribed')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=author).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
