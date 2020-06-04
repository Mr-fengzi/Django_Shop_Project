from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.shortcuts import render

# Create your views here.

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