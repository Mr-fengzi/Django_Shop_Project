import json
from django.core import serializers
from django.http import JsonResponse
from django.views import View

from app.goods.models import Goods


class GoodsListSerializerView(View):
    def get(self,request):
        #通过django的view实现商品列表页
        json_list = []
        #获取所有商品
        goods = Goods.objects.all()
        json_data = serializers.serialize('json',goods)
        json_data = json.loads(json_data)
        #In order to allow non-dict objects to be serialized set the safe parameter to False.
        return JsonResponse(json_data,safe=False)