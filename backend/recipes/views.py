from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from django.shortcuts import get_object_or_404
from .models import Tag, Ingredient, Recipe, Favorite
from .serifalizers import TagSerializer, IngredientSerializer, RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет ингирдиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет рецептов
    Дополнительно переопределен perform_create, куда подтягивается текущий юзер
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(APIView):
    """
    Вьюсет избранных рецептов.
    переопределен метод GET, который проверяет наличие рецепта в избранном и в случае его отсутствия там - добавляет
    Переопределен метод Delete.
    """
    def get(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeSerializer(
            recipe,
            context={'request': request},
        )

        is_favorite = Favorite.objects.get(user=request.user, recipe=recipe).exist()
        if is_favorite:
            return Response(status=HTTP_400_BAD_REQUEST)

        Favorite.objects.create(
            user=request.user,
            recipe=recipe
        )
        return Response(serializer.data)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        result = Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
        if result:
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_404_NOT_FOUND)
