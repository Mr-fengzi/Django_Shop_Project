from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from app.goods.models import Goods
from app.goods.serializers import GoodsSerializer


class GoodsListView(APIView):
    '''
    商品列表
    '''
    def get(self,request,format=None):
        # 获取所有的商品信息
        goods = Goods.objects.all()
        # 根据指定的serializer进行序列化对象
        goods_serialzer = GoodsSerializer(goods,many=True)
        # 以REST需要的Response(状态码和数据信息)返回给用户
        return Response(goods_serialzer.data)