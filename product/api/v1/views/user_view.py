from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from djoser.views import UserViewSet as DjoserUserViewSet

from api.v1.serializers.user_serializer import CustomUserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = (User.objects
                .prefetch_related('in_groups__course')
                .select_related('balance'))
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)
