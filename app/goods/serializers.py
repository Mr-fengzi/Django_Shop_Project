from rest_framework import serializers

# 方法一：Serializer序列化
# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True,max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()

#ModelSerializer实现商品列表页
from app.goods.models import Goods, GoodsCategory, GoodsImage


class CategorySerializer3(serializers.ModelSerializer):
    """三级分类的序列化"""
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class CategorySerializer2(serializers.ModelSerializer):
    """二级分类的序列化"""
    # 在parent_category字段中定义的related_name="sub_cat"
    # many=True代表子分类有多个。否则会报错。
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"

# ModelSerializer实现商品分类列表页(删除原有的代码)
class CategorySerializer(serializers.ModelSerializer):
    """一级分类的序列化"""
    # 一级分类的子分类有多个，many=True
    sub_cat = CategorySerializer2(many = True)

    class Meta:
        model = GoodsCategory
        fields = "__all__"

#轮播图
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ("image",)

class GoodsSerializer(serializers.ModelSerializer):
    #覆盖外键字段，不指定时，只显示分类的id
    category = CategorySerializer()
    # 轮播图的序列化,images是数据库中设置的related_name="images",把轮播图嵌套进来
    images = GoodsImageSerializer(many=True)
    class Meta:
        model = Goods
        # fields = '__all__'  # 需要返回的字段， __all__是所有字段
        exclude = ['goods_desc', ]  # 不显示的字段属性

