from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as my_filters
from rest_framework import status, views, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, TagSerializer)


class LimitFieldPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет ингирдиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (my_filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete']
    filter_backends = (my_filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitFieldPagination

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update'):
            return [IsAuthenticated]
        elif self.action == 'destroy':
            return [IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer


class FavoriteView(views.APIView):
    """
    Вью избранных рецептов.
    переопределен метод GET, который проверяет наличие рецепта в избранном
    и в случае его отсутствия там - добавляет
    """
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk=None):
        user = request.user
        data = {
            'user': user.id,
            'recipe': pk,
        }
        context = {'request': request}
        serializer = FavoriteSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartView(views.APIView):
    """
    Вью добавления в корзину продуктов.
    переопределен метод GET, который проверяет наличие рецепта в корзине
    и в случае его отсутствия там - добавляет
    """
    permission_classes = [IsAuthenticated, ]

    def get(self, request, pk=None):

        user = request.user
        data = {
            'user': user.id,
            'recipe': pk,
        }
        context = {'request': request}
        serializer = ShoppingCartSerializer(data=data, context=context)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCartView(views.APIView):
    def get(self, request):
        items = IngredientInRecipe.objects.select_related(
            'recipe', 'ingredient'
        )
        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session['purchases']
            )

        items = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename{filename}'

        return response
