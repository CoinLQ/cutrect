"""lqcharacter2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
import rect

# -*- coding: utf-8 -*-
import xadmin
xadmin.autodiscover()
from django.urls import path, re_path
# version模块自动注册需要版本控制的 Model
# from xadmin.plugins import xversion
# xversion.register_models()

from django.views.generic import RedirectView

app_name = "cutrect"

urlpatterns = [
    path(r'', RedirectView.as_view(url='/xadmin')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^xadmin/', xadmin.site.urls),
    re_path(r'^api/', include('api.urls')),
    re_path(r'^auth/', include("jwt_auth.urls", namespace="api-auth")),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
