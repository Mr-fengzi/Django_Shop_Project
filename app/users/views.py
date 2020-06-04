from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from ShopProject.settings import APIKEY
from app.users.models import VerifyCode
from app.users.serializers import SmsSerializer
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