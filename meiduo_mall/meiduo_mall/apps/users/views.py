from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponse
from django_redis import get_redis_connection
from users.models import User
import re

class IndexView(View):
    def get(self,request):
        # 获取当前登录的用户
        user=request.user
        return render(request,'index.html')


class UserRegisterView(View):

    def get(self, request):
        # 用户注册
        return render(request, 'register.html')

    def post(self,request):
        # 获取前段传递的表单数据
        data=request.POST
        username=data.get('user_name')
        pwd1=data.get('pwd')
        pwd2=data.get('cpwd')
        mobile=data.get('phone')
        image_code=data.get('pic_code')
        sms_code=data.get('msg_code')
        allow=data.get('allow')

        # 验证表单数据
        if username is None or pwd1 is None or pwd2 is None or mobile is None or image_code is None or sms_code is None or allow is None:
            return render(request, 'register.html', {'error_message': '数据不能为空'})
        # 验证用户名的长度
        if len(username)<5 or len(username)>20:
            return render(request, 'register.html', {'error_message': '长度不符合要求'})
        # 支持手机号注册
        if re.match(r'1[3-9]\d{9}',username):
            if username!=mobile:
                return render(request, 'register.html', {'error_message': '用户名和手机号不一致'})
        # 验证用户名是否存在
        try:
            user=User.objects.get(username=username)
        except:
            user=None

        if user:
            return render(request, 'register.html', {'error_message': '用户存在'})
        # 验证两次密码是否一致
        if pwd1!=pwd2:
            return render(request, 'register.html', {'error_message': '密码不一致'})
        # 验证手机号的格式是否正确
        if not re.match(r'1[3-9]\d{9}',mobile):
            return render(request, 'register.html', {'error_message': '手机格式不正确'})
        if len(mobile)!=11:
            return render(request, 'register.html', {'error_message': '手机格式不正确'})
        # 验证短信验证码的长度
        if len(sms_code)!=6:
            return render(request, 'register.html', {'error_message': '短信验证码不正确'})
        # 去除redis数据库中保存的手机号对应的验证码
        client=get_redis_connection('verfycode')
        real_sms_code=client.get('sms_code_%s'%mobile)

        if real_sms_code is None:
            return render(request,'register.html',{'error_message':'短信验证码失效'})
        if sms_code !=real_sms_code.decode():
            return render(request,'register.html',{'error_message':'短信验证码错误'})
        # 保存数据
        User.objects.create(username=username,mobile=mobile,password=pwd1)

        # 状态保持
        login(request,user)
        return redirect('/index/')

class UserLoginView(View):
    def get(self,request):
        # 渲染返回登录界面
        return render(request,'login.html',{'loginerror':'密码错误'})

    def post(self,request):
        # 登录业务
        data=request.POST
        # 获取数据
        username=data.get('username')
        password=data.get('pwd')
        remembered=data.get('remembered')

        # 用户验证
        user=authenticate(request,username=username,password=password)
        if user is None:
            return render(request,'login.html',{'loginerror':'用户名或密码错误'})

        # 状态保持
        login(request,user)
        # 判断用户是否选择记住登录
        if remembered=='on':
            request.session.set_expiry(60*60*24*7)
            response=redirect('/')
            response.set_cookie('username',username,60*60*24*7)
        else:
            request.session.set_expiry(60*60*2)
            response=redirect('/')
            response.set_cookie('username',username,60*60*2)

        return response

class UserLogoutView(View):
        # 退出登录
    def get(self,request):
        logout(request)
        response=redirect('/login/')
        response.COOKIES.get('username')
        # 删除cookie中的username
        return response