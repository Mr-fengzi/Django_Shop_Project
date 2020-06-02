# -*- coding: utf-8 -*-


import os
import sys


pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + "../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ShopProject.settings")

import django

django.setup()

from app.goods.models import Goods, GoodsCategory, GoodsImage
from app.extra_apps.db_tools.data.product_data import row_data

# 依次遍历商品信息
for goods_detail in row_data:
    # 实例化商品对象;
    goods = Goods()
    goods.name = goods_detail["name"]
    goods.market_price = float(goods_detail["market_price"].replace("￥", "").replace("元", ""))
    goods.shop_price = float(goods_detail["sale_price"].replace("￥", "").replace("元", ""))
    goods.goods_brief = goods_detail["desc"] if goods_detail["desc"] else ""
    goods.goods_desc = goods_detail["goods_desc"] if goods_detail["goods_desc"] else ""

    # 将商品轮播图片的第一张图片作为商品列表页显示的图片
    goods.goods_front_image = goods_detail["images"][0] if goods_detail["images"] else ""

    # 商品的三级分类
    category_name = goods_detail["categorys"][-1]  # 获取到三级分类的名称
    category = GoodsCategory.objects.filter(name=category_name)  # 根据分类名称找到分类对象
    if category:
        goods.category = category[0]
    goods.save()
    print("添加商品 [%s] 成功" % (goods.name))

    # 添加商品图片
    for goods_image in goods_detail["images"]:
        # 创建商品轮播图对象
        goods_image_instance = GoodsImage()
        goods_image_instance.image = goods_image
        # 将商品轮播图对象和商品对象绑定
        goods_image_instance.goods = goods
        goods_image_instance.save()
