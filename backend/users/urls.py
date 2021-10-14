from django.urls import include, path

from .views import CustomAuthToken, FollowUserView, Logout, subscriptions

urlpatterns = [
    path(
        'users/<str:pk>/subscribe/',
        FollowUserView.as_view(),
        name='subscribe',
    ),
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('auth/token/login/', CustomAuthToken.as_view(), 'login'),
    path('auth/token/logout/', Logout.as_view(), 'logout'),
    path('', include('djoser.urls')),
]
