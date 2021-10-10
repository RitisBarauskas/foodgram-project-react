from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow
from .serializers import (AuthTokenSerializer, FollowUsersSerializer,
                          SubscribersSerializer, UserSerializerCustom)

User = get_user_model()


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': str(token)},
            status=status.HTTP_200_OK
        )


class Logout(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class FollowUserViewSet(UserViewSet):

    serializer_class = UserSerializerCustom

    def user_subscribe(self, serializer, id=None):
        following_user = get_object_or_404(User, id=id)

        if self.request.user == following_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.get_or_create(
            user=self.request.user,
            author=following_user
        )

        return Response(FollowUsersSerializer(follow[0]).data)

    def user_unsubscribe(self, serializer, id=None):
        following_user = get_object_or_404(User, id=id)

        deleted_subscriptions = Follow.objects.filter(
            user=self.request.user,
            author=following_user
        ).delete()

        if deleted_subscriptions[0] > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, serializer, id=None):
        if self.request.method == 'DELETE':
            return self.user_unsubscribe(serializer, id)
        else:
            return self.user_subscribe(serializer, id)


@api_view(['get'])
def subscriptions(request):
    user = User.objects.filter(subscribed_by__user=request.user)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(user, request)
    serializer = SubscribersSerializer(
        page,
        many=True,
        context={'current_user': request.user}
    )
    return paginator.get_paginated_response(serializer.data)
