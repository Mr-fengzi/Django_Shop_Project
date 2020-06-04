from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from app.goods.serializers import GoodsSerializer
from app.user_operate.models import UserFav


class UserFavSerializer(serializers.ModelSerializer):
    # 获取当前登录的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserFav
        # 收藏的时候需要返回商品的id,因为取消收藏的时候必须知道商品的id是多少
        fields = ("user", "goods", 'id')
        # validate实现唯一联合,一个商品只能收藏一次,联合验证
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                # message的信息可以自定义
                message="已经收藏"
            )
        ]

class UserFavDetailSerializer(serializers.ModelSerializer):
    '''
    用户收藏详情
    '''
    # 通过商品id获取收藏的商品,需要嵌套商品的序列化
    goods = GoodsSerializer()
    class Meta:
        model = UserFav
        fields = ("goods", "id")