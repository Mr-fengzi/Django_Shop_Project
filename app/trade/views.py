from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from app.trade.models import ShoppingCart, OrderInfo, OrderGoods
from app.trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
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

    # 动态配置serializer
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

        # 在订单提交保存之前还需要多两步步骤,所以这里自定义perform_create方法
        # 1.将购物车中的商品保存到OrderGoods中
        # 2.清空购物车

    def perform_create(self, serializer):
        """序列化验证通过后,执行的内容,默认只是保存序列化的数据, 但此处需要进一步处理"""
        order = serializer.save()
        # 计算订单里面所有商品的总金额: 单价*数量
        sum_money = 0
        # 获取购物车所有商品
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()
            # 一个商品的金额: 单价*数量
            order_goods_money = order_goods.goods.shop_price * order_goods.goods_num
            sum_money += order_goods_money
            # 清空购物车
            shop_cart.delete()


        order.order_mount = sum_money
        order.save()
        return order
