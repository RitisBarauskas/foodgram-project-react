from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomAuthToken, FollowUserViewSet, Logout, subscriptions

router = DefaultRouter()
router.register("", FollowUserViewSet)

urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('auth/token/login/', CustomAuthToken.as_view(), 'login'),
    path('auth/token/logout/', Logout.as_view(), 'logout'),
    path('users/', include(router.urls)),
    path('', include('djoser.urls')),
]
