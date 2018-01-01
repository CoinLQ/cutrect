from rest_framework import mixins, viewsets
from rect.serializers import OColumnSerializer, OPageSerializer, \
                BatchSerializer, PageRectSerializer, RectSerializer, \
                ScheduleSerializer, CCTaskSerializer, ClassifyTaskSerializer, \
                PageTaskSerializer
from rect.models import OColumn, OPage, Batch, PageRect, Rect, \
                        Schedule, CCTask, ClassifyTask, PageTask


class OColumnViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OColumn.objects.all()
    serializer_class = OColumnSerializer


class OPageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OPage.objects.all()
    serializer_class = OPageSerializer


class BatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class PageRectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageRect.objects.all()
    serializer_class = PageRectSerializer


class RectViewSet(viewsets.ModelViewSet):
    queryset = Rect.objects.all()
    serializer_class = RectSerializer


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

