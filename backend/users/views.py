from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow
from .serializers import (AddFollowSerializer, AuthTokenSerializer,
                          SubscribersSerializer)

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


class FollowUserView(APIView):
    """
    Вью создания и удаления подписок.
    """
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk=None):
        user = request.user
        data = {
            'user': user.id,
            'author': pk,
        }
        context = {'request': request}
        serializer = AddFollowSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        serializer = SubscribersSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        Follow.objects.filter(user=user, author=author).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


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
