from rest_framework import mixins, viewsets
from rect.serializers import  PageSerializer, \
                PageRectSerializer, RectSerializer, \
                ScheduleSerializer, CCTaskSerializer, ClassifyTaskSerializer, \
                PageTaskSerializer
from rect.models import Page, PageRect, Rect, \
                        Schedule, CCTask, ClassifyTask, PageTask
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.shortcuts import get_object_or_404
import re

class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class PageRectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageRect.objects.all()
    serializer_class = PageRectSerializer


class RectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rect.objects.all()
    serializer_class = RectSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(Rect, cid=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='col_rects')
    def col_rects(self, request, pk):
        staff = request.user
        rect = get_object_or_404(Rect, cid=pk)
        col_id = rect.cid[:-3]
        pattern = re.compile(r'{}'.format(col_id))
        
        col_rects = list(filter(lambda x: pattern.search(x.cid) and pk != x.cid, Rect.objects.filter(page_code=rect.page_code).all()))
        rects = RectSerializer(data=col_rects, many=True)
        rects.is_valid()
        return Response({"status": 0,
                "rects": rects.data,
                "cid": pk})

class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

