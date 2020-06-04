from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from app.trade.models import ShoppingCart, OrderInfo
from app.trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer
from app.users.permissions import IsUserOrReadOnly


class ShoppingCartViewset(viewsets.ModelViewSet):
    """
    购物车功能
    list:
    获取购物车详情
    delete:
    删除购物记录
    create:
    加入购物车
    """
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ShopCartSerializer
    # 进入详情页更新时查询的关键字
    lookup_field = "goods_id"

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """动态返回序列化类"""
        if self.action == 'list':
            return ShopCartDetailSerializer
        else:
            return ShopCartSerializer


class OrderViewset(viewsets.ModelViewSet):
    """
    订单管理
    list:
    获取个人订单
    delete:
    删除订单
    create:
    新增订单
    """



    permission_classes = (IsAuthenticated, IsUserOrReadOnly)
    # authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer

    # 获取订单列表
    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)
