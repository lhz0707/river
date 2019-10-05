from django.conf.urls import url,include
from django.contrib import admin
from . import views
urlpatterns = [
 # 首页处理
 url(r'^$',views.IndexView.as_view()),
 url(r'^register/$',views.UserRegisterView.as_view()),
 url(r'^login/$', views.UserLoginView.as_view()),
 # 退出登录
 url(r'^logout/$', views.UserLogoutView.as_view()),
]
