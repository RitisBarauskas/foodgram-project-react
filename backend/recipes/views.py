from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_404_NOT_FOUND)
from rest_framework.views import APIView

from .models import Cart, Favorite, Ingredient, IngredientInRecipe, Recipe, Tag
from .serifalizers import IngredientSerializer, RecipeSerializer, TagSerializer


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


class CartViewSet(APIView):
    """
    Вьюсет добавления в корзину продуктов.
    переопределен метод GET, который проверяет наличие рецепта в корзине и в случае его отсутствия там - добавляет
    Переопределен метод Delete.
    """
    def get(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeSerializer(
            recipe,
            context={'request': request},
        )

        is_in_cart = Cart.objects.get(
            user=request.user,
            recipe=recipe
        ).exist()

        if is_in_cart:
            return Response(status=HTTP_400_BAD_REQUEST)

        Cart.objects.create(
            user=request.user,
            recipe=recipe
        )

        return Response(serializer.data)

    def delete(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        result = Cart.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()

        if result:
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_404_NOT_FOUND)


@api_view(['GET', ])
def download_shopping_cart(request):
    """
    Метод загрузки файлов.
    Находим юзера, получаем спиок покупок, связанный с ним.
    Увеличиваем пропорционально на число порций.
    Отдаем файл.
    :param request:
    :return:
    """
    user = request.user
    carts = user.is_in_cart.all()
    for cart in carts:
        ingredients = IngredientInRecipe.objects.filter(
            recipe=cart.recipe
        ).prefetch_related('ingredient')

        for ingredient in ingredients:
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount
            if name in cart.keys():
                cart[name]['amount'] += amount
            else:
                cart[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }

    download_file = ''

    for item in carts:
        download_file += f'{item}: {carts[item]["amount"]} --- {carts[item]["measurement_unit"]}\n'

    response = HttpResponse(
        download_file,
        'Content-Type: text/plain'
    )
    response['Content-Disposition'] = (
        'attachment; filename=shopping_cart.txt'
    )

    return response
