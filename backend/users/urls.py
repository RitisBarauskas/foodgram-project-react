from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomAuthToken, FollowUserViewSet, Logout

app_name = 'users'

router = DefaultRouter()
router.register("users", FollowUserViewSet)
urlpatterns = [
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', Logout.as_view()),
    path('', include('djoser.urls')),
] + router.urls
