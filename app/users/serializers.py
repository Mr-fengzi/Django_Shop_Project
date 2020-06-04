import re
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from rest_framework import serializers

from ShopProject.settings import REGEX_MOBILE
from app.users.models import VerifyCode

User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """用户手机号注册序列化类"""
    mobile = serializers.CharField(max_length=11)

    # 函数名必须:validate + 验证字段名
    def validate_mobile(self, mobile):
        """
       手机号码验证
       """
        # 是否已经注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")
        # 是否合法
        # 判断用户输入的电话号码是否符合正则规则。
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError("手机号码非法")  # 验证码发送频率
        # 60s内只能发送一次: 实质就是判断当前手机号60s之前是否发送过验证码。
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1,
                                                    seconds=0)
        # 从数据库中查询指定手机号码上一次发送验证码的时间大于时间段

        """
       code   add-time     phone
       1233 2020-10-10 10:01:00 18829267777
 
       当前时间: 20220-10-10 11:00:00
       当前时间: 20220-10-10 10:01:30   === 10:00:30
       """
        if VerifyCode.objects.filter(add_time__gt=one_mintes_ago,
                                     mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送未超过60s")
        return mobile