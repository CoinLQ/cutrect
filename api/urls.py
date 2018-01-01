# -*- coding: UTF-8 -*-
from django.conf.urls import url, include

from rest_framework import routers

from .views.rects import BatchViewSet, PageRectViewSet, RectViewSet, \
                        ScheduleViewSet, OPageViewSet, OColumnViewSet
from .views.tasks import CCTaskViewSet, ClassifyTaskViewSet, \
                         PageTaskViewSet

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
rectRouter.register(r'opage', OPageViewSet)
rectRouter.register(r'ocolumn', OColumnViewSet)


urlpatterns = [
    url(r'^', include(rectRouter.urls)),
]









