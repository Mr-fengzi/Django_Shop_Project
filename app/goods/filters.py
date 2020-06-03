import django_filters
from django.db.models import Q

from app.goods.models import Goods


class GoodsFilter(django_filters.rest_framework.FilterSet):
    '''
   商品过滤的类
   '''
    # 两个参数,name是要过滤的字段,lookup是执行的行为,‘小与等于本店价格’
    price_min = django_filters.NumberFilter(field_name="shop_price",
                                            lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name="shop_price",
                                            lookup_expr='lte')
    top_category = django_filters.NumberFilter(field_name='category', method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        # 不管当前点击的是一级分类二级分类还是三级分类,都能找到。
        return queryset.filter(Q(category_id=value) |
                               Q(category__parent_category_id=value) |
                               Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        fields = ['price_min', 'price_max']