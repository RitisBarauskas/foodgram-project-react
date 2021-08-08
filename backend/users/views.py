from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
from .models import User


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
