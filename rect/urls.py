# -*- coding: UTF-8 -*-

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve #处理静态文件
from rest_framework import routers
from rect.views import BatchViewSet, PageRectViewSet, RectViewSet, ScheduleViewSet, CCTaskViewSet, ClassifyTaskViewSet, PageTaskViewSet
from rect.views import CreateScheduleView, UploadBatchView

import xadmin
# xadmin.autodiscover()

# version模块自动注册需要版本控制的 Model
from xadmin.plugins import xversion
xversion.register_models()

router = routers.DefaultRouter()
router.register(r'batch', BatchViewSet)
router.register(r'pagerect', PageRectViewSet)
router.register(r'rect', RectViewSet)
router.register(r'schedule', ScheduleViewSet)
router.register(r'cctask', CCTaskViewSet)
router.register(r'classifytask', ClassifyTaskViewSet)
router.register(r'pagetask', PageTaskViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^create_schedule', CreateScheduleView.as_view(), name='create_schedule'),
    url(r'^upload_batch', UploadBatchView.as_view(), name='upload_batch')
]









