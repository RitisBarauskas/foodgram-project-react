from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, RecipeViewSet, IngredientViewSet, FavoriteViewSet, CartViewSet


router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('<str:pk>/shopping_cart/', CartViewSet.as_view(), name='shopping_cart'),
    path('<str:pk>/favorite/', FavoriteViewSet.as_view(), name='favorite'),
    path('', include(router.urls)),
]
