from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from app.user_operate.models import UserFav, UserLeavingMessage
from app.user_operate.serializers import UserFavSerializer, UserFavDetailSerializer, LeavingMessageSerializer
from app.users.permissions import IsUserOrReadOnly


class UserFavViewset(viewsets.GenericViewSet, mixins.ListModelMixin,
                     mixins.CreateModelMixin, mixins.DestroyModelMixin):
    '''
    用户收藏
    '''
    # queryset = UserFav.objects.all()
    #serializer_class = UserFavSerializer

    # permission是用来做权限判断的
    # IsAuthenticated:必须登录用户;IsUserOrReadOnly:必须是当前登录的用户
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # # auth使用来做用户认证的
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    # 搜索的字段，当访问收藏详细信息/删除商品收藏时，根据商品id进行操作。
    lookup_field = 'goods_id'

    # 动态选择serializer
    def get_serializer_class(self):
        if self.action == "list":
            return UserFavDetailSerializer
        elif self.action == "create":
            return UserFavSerializer
        return UserFavSerializer

    def get_queryset(self):
        # 只能查看当前登录用户的收藏,不会获取所有用户的收藏
        return UserFav.objects.filter(user=self.request.user)


class LeavingMessageViewset(mixins.ListModelMixin, mixins.DestroyModelMixin,
                            mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    list:
    获取用户留言
    create:
    添加留言
    delete:
    删除留言功能
    """
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = LeavingMessageSerializer

    # 只能看到自己的留言
    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)
