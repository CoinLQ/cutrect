# -*- coding: UTF-8 -*-

from django.conf import settings
from django.conf.urls import url, include

from rest_framework import routers

from rect.views import BatchViewSet, PageRectViewSet, RectViewSet, ScheduleViewSet, CCTaskViewSet, ClassifyTaskViewSet, PageTaskViewSet
from rect.views import CreateScheduleView, UploadBatchView


from xadmin.plugins import xversion
xversion.register_models()

rectRouter = routers.DefaultRouter()
rectRouter.register(r'batch', BatchViewSet)
rectRouter.register(r'pagerect', PageRectViewSet)
rectRouter.register(r'rect', RectViewSet)
rectRouter.register(r'schedule', ScheduleViewSet)
rectRouter.register(r'cctask', CCTaskViewSet)
rectRouter.register(r'classifytask', ClassifyTaskViewSet)
rectRouter.register(r'pagetask', PageTaskViewSet)


urlpatterns = [
    url(r'^rect/', include(rectRouter.urls)),
    url(r'^rect/create_schedule', CreateScheduleView.as_view(), name='create_schedule'),
    url(r'^rect/upload_batch', UploadBatchView.as_view(), name='upload_batch')
]









