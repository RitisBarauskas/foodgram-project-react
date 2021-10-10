from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartView, FavoriteView, IngredientViewSet,
                    RecipesViewSet, ShoppingCartView, TagViewSet, add_ing)

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path(
        'add_ing/',
        add_ing,
        name='add-ing',
    ),
    path(
        'recipes/<str:pk>/favorite/',
        FavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/<str:pk>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartView.as_view(),
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
]
