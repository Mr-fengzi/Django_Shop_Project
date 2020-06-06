from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app.goods.filters import GoodsFilter
from app.goods.models import Goods, GoodsCategory, Banner
from app.goods.serializers import GoodsSerializer, CategorySerializer, BannerSerializer


# class GoodsListView(APIView):
#     '''
#     商品列表
#     '''
#     def get(self,request,format=None):
#         # 获取所有的商品信息
#         goods = Goods.objects.all()
#         # 根据指定的serializer进行序列化对象
#         goods_serialzer = GoodsSerializer(goods,many=True)
#         # 以REST需要的Response(状态码和数据信息)返回给用户
#         return Response(goods_serialzer.data)

class GoodsPagination(PageNumberPagination):
   '''
  商品列表自定义分页
  '''
   # 默认每页显示的个数
   page_size = 10
   # 可以动态改变每页显示的个数 # http://xxxx/goods/?page=2&page_size=5
   page_size_query_param = 'page_size'
   # 页码参数
   page_query_param = 'page'  # http://xxxx/goods/?page=1
   # 最多能显示多少页
   max_page_size = 100

class GoodsListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
   """
  商品列表页
  """
   # 分页
   pagination_class = GoodsPagination
   queryset = Goods.objects.all().order_by('id')
   serializer_class = GoodsSerializer

   filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)

   # 设置filter的类为我们自定义的类
   filter_class = GoodsFilter

   # 搜索,=name表示精确搜索,也可以使用各种正则表达式
   search_fields = ('=name', 'goods_brief')

   # 排序
   ordering_fields = ('sold_num', 'add_time')

   def retrieve(self, request, *args, **kwargs):
      """重写retrieve方法"""
      instance = self.get_object()
      instance.click_num += 1
      instance.save()
      serializer = self.get_serializer(instance)
      return Response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
   '''
   list:
   商品分类列表数据
   '''
   # queryset = GoodsCategory.objects.all()
   # 希望查询一级分类的信息
   queryset = GoodsCategory.objects.filter(category_type = 1)
   serializer_class = CategorySerializer


class BannerViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
   """
   首页轮播图
   """
   queryset = Banner.objects.all().order_by("index")
   serializer_class = BannerSerializer

