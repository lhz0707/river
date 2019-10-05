from django.contrib.auth.backends import ModelBackend
import re
from users.models import User
class UserUtils(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断用户是否有手机号注册
        try:
            if re.match(r'1[3-9]\d{9}]',username):
                user=User.object.get(mobile=username)
            else:
                user=User.objects.get(username=username)
        except:
            user=None

        # 查询数据对象的校验码是否正确
        if user is not None and user.check_password(password):
            return user