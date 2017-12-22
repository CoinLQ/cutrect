# -*- coding: UTF-8 -*-

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve #处理静态文件
from rest_framework import routers
from . import views

import xadmin
# xadmin.autodiscover()

# version模块自动注册需要版本控制的 Model
from xadmin.plugins import xversion
xversion.register_models()

router = routers.DefaultRouter()
router.register(r'batch', views.BatchViewSet)
router.register(r'pagerect', views.PageRectViewSet)
router.register(r'rect', views.RectViewSet)
router.register(r'schedule', views.ScheduleViewSet)
router.register(r'task', views.TaskViewSet)
router.register(r'patch', views.PatchViewSet)
router.register(r'user', views.UserViewSet)
router.register(r'group', views.GroupViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
]









