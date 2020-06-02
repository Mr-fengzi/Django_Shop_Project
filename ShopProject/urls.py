"""ShopProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from rest_framework.documentation import include_docs_urls

from ShopProject.settings import MEDIA_ROOT
from app.goods.views import GoodsListView
from app.goods.views_serializer import GoodsListSerializerView

urlpatterns = [
    # path('admin/', admin.site.urls),
    # 使用xadmin进行后台的管理
    path('xadmin/', xadmin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    path('media/<path:path>',serve,{'document_root':MEDIA_ROOT}),
    # path('goods1/',GoodsListView.as_view(),name='goods-list-django'),
    # path('goods2/',GoodsListSerializerView.as_view(),name='goods-list-serializer'),
    path('api-auth/',include('rest_framework.urls')),
    # drf文档,title自定义, 如果要实现API文档页展示,需要在settings文件中配置。
    path('docs', include_docs_urls(title='Young RESTful Docs')),
    # 商品列表页, 删除前两种商品列表页的url配置.
    path('goods/', GoodsListView.as_view(), name='goods-list-rest')
]
