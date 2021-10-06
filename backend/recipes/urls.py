from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet, download_shopping_cart)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register('tags', TagViewSet, basename='tags')
router.register('', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('tags/', TagViewSet, name='tags'),
    path('recipes/download_shopping_cart/', download_shopping_cart, name='download_shopping_cart'),
    path('recipes/<str:pk>/shopping_cart/', CartViewSet.as_view(), name='shopping_cart'),
    path('recipes/<str:pk>/favorite/', FavoriteViewSet.as_view(), name='favorite'),
    path('recipes/', include(router.urls)),
]
