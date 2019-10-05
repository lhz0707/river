from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageView.as_view()),
    url(r'^sms_codes/(?P<mobile>\w+)/$', views.SmsCodeView.as_view()),
    url(r'^usernames/(?P<username>\w+)/count/$', views.UsernameCount.as_view()),
    url(r'^mobiles/(?P<mobile>\w+)/count/$', views.MobileCount.as_view()),

]
