from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .models import Favorite, Ingredient, IngredientInRecipe, Recipe, Tag
from .serializers import IngredientSerializer, TagSerializer, RecipeCreateUpdateSerializer, RecipeMinifieldSerializer, RecipeListSerializer
from .mixins import CreateAndDeleteRelatedMixin


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет тегов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет ингирдиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Ingredient.objets
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset.all()


class RecipesViewSet(viewsets.ModelViewSet, CreateAndDeleteRelatedMixin):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in (
            'shopping_cart',
            'favorite',
            'download_shopping_cart'
        ):
            return [IsAuthenticated]
        elif self.action == 'destroy':
            return [IsAuthenticatedOrReadOnly]
        else:
            return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        elif self.action in ('shopping_cart', 'favorite'):
            return RecipeMinifieldSerializer
        else:
            return RecipeListSerializer

    def get_queryset(self):
        tags = self.request.query_params.getlist('tags')
        user = self.request.user
        queryset = Recipe.objects
        if tags:
            queryset = queryset.filter_by_tags(tags)
        queryset = queryset.add_user_annotations(user.pk)
        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(is_favorited=True)
        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(in_shopping_cart=True)
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author=author)

        return queryset

    @action(methods=['get', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.create_and_delete_related(
            pk=pk,
            klass=Favorite,
            create_fqiled_message="Не удалось добавить рецепт в список покупок",
            delete_failed_message="Рецепт отсутствует в списке покупок",
            field_to_create_or_delete_name='recipe'
        )

    @action(methods=['get', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return self.create_and_delete_related(
            pk=pk,
            klass=Favorite,
            create_fqiled_message="Не удалось добавить рецепт в избранное",
            delete_failed_message="Рецепт отсутствует в избранном",
            field_to_create_or_delete_name='recipe'
        )

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
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
