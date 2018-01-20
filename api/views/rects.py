from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rect.serializers import  PageSerializer, \
                PageRectSerializer, RectSerializer, \
                ScheduleSerializer, CCTaskSerializer, ClassifyTaskSerializer, \
                PageTaskSerializer
from rect.models import Page, PageRect, Rect, \
                        Schedule, CCTask, ClassifyTask, PageTask

from api.pagination import StandardPagination



class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class PageRectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PageRect.objects.all()
    serializer_class = PageRectSerializer


class RectResultsSetPagination(StandardPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class RectViewSet(viewsets.ModelViewSet, mixins.ListModelMixin):
    queryset = Rect.objects.all()
    serializer_class = RectSerializer
    pagination_class = RectResultsSetPagination

    @list_route(methods=['get'], url_path='ccreview')
    def ccreview(self, request):
        schedule_id = self.request.query_params.get('schedule_id', None)
        cc = self.request.query_params.get('cc', 0.96)
        #page = self.request.query_params.get('page', 1)
        #page_size = self.request.query_params.get('page_size', 20)
        try:
            schedule = Schedule.objects.get(pk=schedule_id)
        except Schedule.DoesNotExist:
            return Response({"status": -1,
                             "msg": "not found schedule instance!"})

        reelRids = [reel.rid for reel in schedule.reels.all()]
        if len(reelRids) <= 0 :
            return Response({"status": -1,
                             "msg": "The schedule does not select reels!"})
        rects = Rect.objects.filter(reel__in=reelRids, cc__lte=cc).order_by("-cc")

        page = self.paginate_queryset(rects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(rects, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

