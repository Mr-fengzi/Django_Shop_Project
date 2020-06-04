import time

from rest_framework import serializers

from app.goods.models import Goods
from app.goods.serializers import GoodsSerializer
from app.trade.models import ShoppingCart, OrderInfo, OrderGoods


class ShopCartSerializer(serializers.Serializer):
    # 获取当前登录的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    nums = serializers.IntegerField(required=True, label="数量", min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于一",
                                        "required": "请选择购买数量"
                                    })
    # 这里是继承Serializer,必须指定queryset对象,如果继承ModelSerializer则不需要指定
    # goods是一个外键,可以通过这方法获取goods object中所有的值
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())

    # 继承的Serializer没有save功能,必须写一个create方法
    def create(self, validated_data):
        # validated_data是已经处理过的数据
        # 获取当前用户
        # view中:self.request.user;serizlizer中:self.context["request"].user
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        # 如果购物车中有记录,数量+1
        # 如果购物车车没有记录,就创建
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            # 添加到购物车，**validated_data 解包
            existed = ShoppingCart.objects.create(**validated_data)
        return existed

    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        # 保存到数据库中
        instance.save()
        # 将新的对象返回
        return instance


class ShopCartDetailSerializer(serializers.ModelSerializer):
    '''
    购物车商品详情信息
    '''
    # 一个购物车对应一个商品
    goods = GoodsSerializer(many=False, read_only=True)
    class Meta:
        model = ShoppingCart
        fields = ("goods", "nums")


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()

    )
    # 生成订单的时候这些不用post
    # 订单状态
    pay_status = serializers.CharField(read_only=True)
    # 订单号一定要唯一(unique=True)
    order_sn = serializers.CharField(read_only=True)
    # 支付时间
    pay_time = serializers.DateTimeField(read_only=True)
    # 订单的支付类型
    pay_type = serializers.CharField(read_only=True)
    # 支付宝交易号
    trade_no = serializers.CharField(read_only=True)
    # 微信支付会用到
    nonce_str = serializers.CharField(read_only=True)
    # 订单添加时间是只读的
    add_time = serializers.DateTimeField(read_only=True)
    # 订单的金额是只读的
    order_mount = serializers.FloatField(read_only=True)

    def generate_order_sn(self):
        # 生成订单号
        # 当前时间 + userid + 随机数
        from random import Random
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(
            time_str=time.strftime("%Y%m%d%H%M%S"),
            userid=self.context["request"].user.id,
            ranstr=random_ins.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        # validate中添加order_sn,然后在view中就可以save
        attrs["order_sn"] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = "__all__"
        
        
# 订单中的商品
class OrderGoodsSerialzier(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = "__all__"

# 订单商品信息
# goods字段需要嵌套一个OrderGoodsSerializer
class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerialzier(many=True)
    class Meta:
        model = OrderInfo
        fields = "__all__"

# 订单商品信息
# goods字段需要嵌套一个OrderGoodsSerializer
class OrderDetailSerializer(serializers.ModelSerializer):
   goods = OrderGoodsSerialzier(many=True)
   class Meta:
       model = OrderInfo
       fields = "__all__"