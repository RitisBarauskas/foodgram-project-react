from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CartViewSet, FavoriteViewSet, IngredientViewSet,
                    RecipeViewSet, TagViewSet, download_shopping_cart)

router = DefaultRouter()
router_2 = DefaultRouter()
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('', RecipeViewSet, basename='recipes')
router_2.register('', TagViewSet, basename='ingredients')

urlpatterns = [

    path('recipes/download_shopping_cart', download_shopping_cart,
         name='download_shopping_cart'),
    path('recipes/<str:pk>/shopping_cart/', CartViewSet.as_view(),
         name='shopping_cart'),
    path('recipes/<str:pk>/favorite/', FavoriteViewSet.as_view(),
         name='favorite'),
    path('recipes/', include(router.urls)),
    path('tags/', include(router_2.urls)),
]
