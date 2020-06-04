import re
from datetime import datetime, timedelta

import pytz
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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


class UserRegSerializer(serializers.ModelSerializer):
    '''
    用户注册
    '''
    # UserProfile中没有code字段,这里需要自定义一个code序列化字段
    code = serializers.CharField(required=True,
                                write_only=True,
                                min_length=4,
                                max_length=6,
                                error_messages={
                                    "blank": "请输入验证码",
                                    "required": "请输入验证码",
                                    "max_length": "验证码格式错误",
                                    "min_length": "验证码格式错误"
                                },
                                help_text="验证码")
    # 验证用户名是否存在
    username = serializers.CharField(label="用户名",
                                    help_text="用户名",
                                    required=True,
                                    allow_blank=False,
                                    validators=[UniqueValidator(queryset=User.objects.all(),  message="用户已经存在")])

    # 输入密码的时候不显示明文
    password = serializers.CharField(style={'input_type': 'password'},
                                     label="密码", write_only=True)
    # 验证code
    def validate_code(self, code):
        # 用户注册,已post方式提交注册信息,post的数据都保存在initial_data里面
        # username就是用户注册的手机号,验证码按添加时间倒序排序,为了后面验证过期,错误等
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data["username"]).order_by("-add_time")
        if verify_records:
            # 最近的一个验证码
            last_record = verify_records[0]
            # 有效期为五分钟。
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            print(five_mintes_ago)
            print(last_record.add_time)
            # +timedelta(hours=8) 是因为时区不同，就加8个小时；
            # 对比的两个时间不属于同一类型，now就是一个offset-naive型即不含时区的类型，now.replace(tzinfo=pytz.timezone('UTC'))可以转换成含时区的offset-aware型
            # .replace(tzinfo=None) 可以将offset-aware型转换为offset-naive型
            if five_mintes_ago > (last_record.add_time+timedelta(hours=8)).replace(tzinfo=None):
                raise serializers.ValidationError("验证码过期")
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    # 所有字段。attrs是字段验证合法之后返回的总的dict
    def validate(self, attrs):
        # 前端没有传mobile值到后端,这里添加进来
        attrs["mobile"] = attrs["username"]
        # code是自己添加得,数据库中并没有这个字段,验证完就删除掉
        del attrs["code"]
        return attrs

    # 密码加密保存
    def create(self, validated_data):
        user = super(UserRegSerializer,
                     self).create(validated_data=validated_data)
        # 对于明文密码进行加密
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'code', 'mobile', 'password')