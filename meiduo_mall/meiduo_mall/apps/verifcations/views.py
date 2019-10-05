from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from random import randint

from meiduo_mall.libs.captcha.captcha import Captcha
from meiduo_mall.libs.yuntongxun.sms import CCP
from users.models import User
from celery_tasks.code_sms.tasks import send_sms_code
from threading import Thread

class ImageView(View):
    # 图片验证码
    def get(self,request,uuid):
        # 生成图片验证吗
        captcha=Captcha.instance()
        data,text,image=captcha.generate_captcha()
        # 将图片数据存储到redis中
        client=get_redis_connection('verfycode')
        client.setex('image_code_%s' % uuid, 60 * 5, text)
        # 返回验证码图片
        return HttpResponse(image,content_type='image/jpg')

class SmsCodeView(View):
    def get(self,request,mobile):
        # 发送短信
        client=get_redis_connection('verfycode')
        # 判断两次的请求时间间隔是否在60秒内
        flag_data=client.get('sms_flag_%s'%mobile)
        if flag_data:
            return HttpResponse('请求过于频繁',status=400)
        # 获取前段数据
        image_code=request.GET.get('image_code')
        uuid=request.GET.get('image_code_id')

        # 生成短信数据
        sms_code='%06d'%randint(0,999999)
        print(sms_code)

        # 获取图片验证吗
        client=get_redis_connection('verfycode')
        real_code=client.get('image_code_%s'%uuid)
        if real_code is None:
            return HttpResponse('图片验证码失效',status=400)
        if image_code.lower()!=real_code.decode().lower():
            return HttpResponse('验证码错误')

        # 发送短信
        send_sms_code.delay(mobile,sms_code)

        # 保存生成的短信验证码到redis
        pipline=client.pipeline()
        pipline.setex('sms_code_%s'%mobile,60*5,sms_code)
        pipline.setex('sms_flag_%s'%mobile,60,123)
        # 适应管道发送数据
        pipline.excute()
        return  JsonResponse({'code':'0'})

# 判断用户名是否重复
class UsernameCount(View):
    def get(self,request,username):
        # 获取前段传递的用户信息
        count=User.objects.filter(username=username).count()

        return JsonResponse({'count':count})

class MobileCount(View):
    # 判断手机号是否重复
    def get(self,request,mobile):
        count=User.objects.filter(mobile=mobile).count()
        return JsonResponse({'count':count})