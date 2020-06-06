from datetime import datetime

from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ShopProject.settings import APPID, private_key_path, ali_pub_key_path
from app.trade.models import ShoppingCart, OrderInfo, OrderGoods
from app.trade.serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from app.trade.utils import AliPay
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


class AlipayView(APIView):
    def get(self, request):
        """
       处理支付宝的return_url返回
       """
        processed_dict = {}
        # 1. 获取GET中参数
        for key, value in request.GET.items():
            processed_dict[key] = value
        # 2. 取出sign
        sign = processed_dict.pop("sign", None)
        # 3. 生成ALipay对象
        alipay = AliPay(
            appid=APPID,
            app_notify_url="http://118.190.210.92:8000/alipay/return/",
            app_private_key_path=private_key_path,
            alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://118.190.210.92:8000/alipay/return/"
        )
        verify_re = alipay.verify(processed_dict, sign)
        # 这里可以不做操作。因为不管发不发return url。notify url都会修改订单状态。
        # if verify_re is True:
        #     order_sn = processed_dict.get('out_trade_no', None)
        #     trade_no = processed_dict.get('trade_no', None)
        #     trade_status = processed_dict.get('trade_status', None)
        #     existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
        #     for existed_order in existed_orders:
        #         existed_order.pay_status = trade_status
        #         existed_order.trade_no = trade_no
        #         existed_order.pay_time = datetime.now()
        #         existed_order.save()

        return Response('success')

    def post(self, request):
        """
       处理支付宝的notify_url
       """
        # 存放post里面所有的数据
        processed_dict = {}
        # 取出post里面的数据
        for key, value in request.POST.items():
            processed_dict[key] = value
        # 把signpop掉,文档有说明
        sign = processed_dict.pop("sign", None)
        # 3. 生成ALipay对象
        alipay = AliPay(
            appid=APPID,
            app_notify_url="http://118.190.210.92:8000/alipay/return/",
            app_private_key_path=private_key_path, alipay_public_key_path=ali_pub_key_path,
            debug=True,  # 默认False,
            return_url="http://118.190.210.92:8000/alipay/return/"

        )
        # 进行验证
        verify_re = alipay.verify(processed_dict, sign)
        # 如果验签成功
        if verify_re is True:
            # 商户网站唯一订单号
            order_sn = processed_dict.get('out_trade_no', None)
            # 支付宝系统交易流水号
            trade_no = processed_dict.get('trade_no', None)
            # 交易状态
            trade_status = processed_dict.get('trade_status', None)
            # 查询数据库中订单记录
            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                # 订单商品项
                order_goods = existed_order.goods.all()
                # 商品销量增加订单中数值
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()
                # 更新订单状态
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()
            # 需要返回一个'success'给支付宝,如果不返回,支付宝会一直发送订单支付成功的消息
            return Response("success")