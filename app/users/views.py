from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, mixins, authentication, permissions
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from ShopProject.settings import APIKEY
from app.users.models import VerifyCode
from app.users.serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from app.users.sms import YunPian

User = get_user_model()
class CustomBackend(ModelBackend):
    """
      自定义用户验证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 用户名和手机都能登录，如果用户输入用户名或者手机号和密码登录均可
            user = User.objects.get(
                Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(CreateModelMixin, viewsets.GenericViewSet):
    '''
    手机验证码
    '''
    serializer_class = SmsSerializer

    def create(self, request, *args, **kwargs):
        """重写create方法"""
        serializer = self.get_serializer(data=request.data)
        # 验证合法
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]

        yun_pian = YunPian(APIKEY)

        # 生成验证码
        code = yun_pian.generate_code()

        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)

class UserViewset(CreateModelMixin, mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin, viewsets.GenericViewSet):
    '''
    用户
    '''
    # serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication,
                            authentication.SessionAuthentication)
    # 这里需要动态权限配置
    # 1.用户注册的时候不应该有权限限制
    # 2.当想获取用户详情信息的时候,必须登录才行
    def get_permissions(self):
        # 执行的操作: get: list, post: create
        if self.action == "retrieve" :
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        return []
    # 这里需要动态选择用哪个序列化方式
    # 1.UserRegSerializer(用户注册),只返回username和mobile,会员中心页面需要显示更多字段,所以要创建一个UserDetailSerializer
    # 2.问题又来了,如果注册的使用userdetailSerializer,又会导致验证失败,所以需要动态的使用serializer
    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "update":
            return UserDetailSerializer
        elif self.action == "create":
            return UserRegSerializer
        return UserDetailSerializer

    # 虽然继承了Retrieve可以获取用户详情,但是并不知道用户的id,所有要重写get_object方法
    # 重写get_object方法,就知道是哪个用户了
    def get_object(self):
        return self.request.user