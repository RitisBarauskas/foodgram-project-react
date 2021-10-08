from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet, download_shopping_cart)

router = DefaultRouter()
router.register('recipes/ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/download_shopping_cart/', download_shopping_cart,
         name='download_shopping_cart'),
    path('recipes/<str:pk>/shopping_cart/', CartViewSet.as_view(),
         name='shopping_cart'),
    path('recipes/<str:pk>/favorite/', FavoriteViewSet.as_view(),
         name='favorite'),
    path('', include(router.urls)),
]
