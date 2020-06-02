import xadmin
from django.contrib import admin

# Register your models here.
from app.goods.models import GoodsImage, GoodsCategory, Goods, Banner, GoodsCategoryBrand, HotSearchWords, IndexAd


class GoodsAdmin(object):
    # 显示的列
    list_display = ["name", "click_num", "sold_num", "fav_num", "goods_num",
    "market_price","shop_price", "goods_brief",  "is_new", "is_hot",
    "add_time"]
    # 可以搜索的字段
    search_fields = ['name', ]
    # 列表页可以直接编辑的
    list_editable = ["is_hot", ]
    # 过滤器
    list_filter = ["name", "click_num", "sold_num", "fav_num", "goods_num",
    "market_price","shop_price", "is_new", "is_hot", "add_time",
    "category__name"]
    # 富文本编辑器
    style_fields = {"goods_desc": "ueditor"}
    # 在添加商品的时候可以添加商品图片

    class GoodsImagesInline(object):
        model = GoodsImage
        # 不显示的字段名称
        exclude = ["add_time"]
        # 控制初始表单数量,默认为3
        extra = 3
        style = 'tab'

    inlines = [GoodsImagesInline]


class GoodsCategoryAdmin(object):
    """商品分类的后台设置"""
    list_display = ["name", "category_type", "parent_category", "add_time"]
    list_filter = ["category_type", "parent_category", "name"]
    search_fields = ['name', ]


class GoodsBrandAdmin(object):
    # list_display = ["category", "image", "name", "desc"]
    list_display = ["image", "name", "desc"]

    # def get_context(self):
    #     context = super(GoodsBrandAdmin, self).get_context()
    #     if 'form' in context:
    #         context['form'].fields['category'].queryset = GoodsCategory.objects.filter(category_type=1)
    #     return context

class BannerGoodsAdmin(object):
    # list_display = ["goods", "image", "index"]
    list_display = ["image", "index"]

class HotSearchAdmin(object):
    list_display = ["keywords", "index", "add_time"]

class IndexAdAdmin(object):
    # list_display = ["category", "goods"]
    list_display = ["goods"]

xadmin.site.register(Goods, GoodsAdmin)
xadmin.site.register(GoodsCategory, GoodsCategoryAdmin)
xadmin.site.register(Banner, BannerGoodsAdmin)
xadmin.site.register(GoodsCategoryBrand, GoodsBrandAdmin)
xadmin.site.register(HotSearchWords, HotSearchAdmin)
xadmin.site.register(IndexAd, IndexAdAdmin)
