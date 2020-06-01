from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

# Create your models here.
class UserProfile(AbstractUser):
    """用户信息"""
    GENDER_CHOICES = (
        ("male", "男"),
        ("female", "女")

    )
    # 用户用手机注册,所以姓名,生日和邮箱可以为空
    name = models.CharField("姓名", max_length=30, null=True, blank=True)
    birthday = models.DateField("出生年月", null=True, blank=True)
    gender = models.CharField("性别", max_length=6, choices=GENDER_CHOICES,
                              default="female")
    """
   null 是针对数据库而言,如果 null=True, 表示数据库的该字段可以为空。
   blank 是针对表单的,如果 blank=True,表示你的表单填写该字段的时候可以不填
   """
    mobile = models.CharField("电话", max_length=11, null=True, blank=True)
    email = models.EmailField("邮箱", max_length=100, null=True, blank=True)

    # 元数据操作
    class Meta:
        # 后台管理显示单数和复数的名称
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class VerifyCode(models.Model):
   """验证码"""
   code = models.CharField("验证码", max_length=10)
   mobile = models.CharField("电话", max_length=11)
   add_time = models.DateTimeField("添加时间", default=datetime.now)

   class Meta:
       verbose_name = "短信验证"
       verbose_name_plural = verbose_name

   def __str__(self):
       return self.code