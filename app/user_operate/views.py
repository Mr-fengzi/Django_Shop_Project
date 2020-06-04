from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins

from app.user_operate.models import UserFav
from app.user_operate.serializers import UserFavSerializer, UserFavDetailSerializer


class UserFavViewset(viewsets.GenericViewSet, mixins.ListModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin):
    '''
    用户收藏
    '''
    queryset = UserFav.objects.all()
    #serializer_class = UserFavSerializer

    # 动态选择serializer
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializer
        return UserFavSerializer