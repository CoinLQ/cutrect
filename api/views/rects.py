from rest_framework import mixins, viewsets
from rect.serializers import OColumnSerializer, PageSerializer, \
                PageRectSerializer, RectSerializer, \
                ScheduleSerializer, CCTaskSerializer, ClassifyTaskSerializer, \
                PageTaskSerializer
from rect.models import OColumn, Page, PageRect, Rect, \
                        Schedule, CCTask, ClassifyTask, PageTask


class OColumnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OColumn.objects.all()
    serializer_class = OColumnSerializer


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class PageRectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageRect.objects.all()
    serializer_class = PageRectSerializer


class RectViewSet(viewsets.ModelViewSet):
    queryset = Rect.objects.all()
    serializer_class = RectSerializer


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

