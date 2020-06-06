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
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token

from ShopProject.settings import MEDIA_ROOT
from app.goods.views import GoodsListViewSet, CategoryViewSet, BannerViewset
from app.goods.views_serializer import GoodsListSerializerView
from app.trade.views import ShoppingCartViewset, OrderViewset, AlipayView
from app.user_operate.views import UserFavViewset, LeavingMessageViewset, AddressViewset
from app.users.views import SmsCodeViewset, UserViewset

router = DefaultRouter()
# 配置goods的url, 自动生成路由和视图函数的对应关系。
"""
^goods/$ [name='goods-list']
^goods\.(?P<format>[a-z0-9]+)/?$ [name='goods-list']
^goods/(?P<pk>[^/.]+)/$ [name='goods-detail']
^goods/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='goods-detail']
"""
router.register(r'goods', GoodsListViewSet, basename='goods')
# 配置Category的url
router.register(r'categorys', CategoryViewSet, basename="categorys")

# 配置codes的url
router.register(r'code', SmsCodeViewset, basename="code")
# 配置users的url
router.register(r'users', UserViewset, basename="users")

# 配置用户收藏的url
router.register(r'userfavs', UserFavViewset, basename="userfavs")

# 用户留言的url, basename是视图函数的别名
router.register(r'messages', LeavingMessageViewset, basename="messages")

# 配置收货地址
router.register(r'address', AddressViewset, basename="address")

# 配置购物车的url
router.register(r'shopcarts', ShoppingCartViewset, basename="shopcarts")

# 配置订单的url
router.register(r'orders', OrderViewset, basename="orders")

# 配置首页轮播图的url
router.register(r'banners', BannerViewset, basename="banners")

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
    path('docs/', include_docs_urls(title='Young RESTful Docs')),
    # 商品列表页, 删除前两种商品列表页的url配置.
    # path('goods/', GoodsListView.as_view(), name='goods-list-rest')
    # token
    # path('api-token-auth/', views.obtain_auth_token)
    # jwt的token认证接口
    path('jwt-auth/', obtain_jwt_token ),
    # 配置支付宝支付的url
    path('alipay/return/', AlipayView.as_view()),
]

# 将DefaultRouter注册的路由和视图函数对应关系添加到urlpatterns里面。
urlpatterns += router.urls
