from rest_framework import serializers
from .models import User, Follow


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }
