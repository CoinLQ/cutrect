from rest_framework import mixins, viewsets
from rect.serializers import CCTaskSerializer, ClassifyTaskSerializer, \
                PageTaskSerializer
from api.serializer import RectSerializer, PageRectSerializer
from rect.models import CCTask, ClassifyTask, PageTask, Rect, PageRect, OpStatus
from rest_framework.response import Response
from rest_framework.decorators import detail_route, list_route
from api.utils.task import retrieve_cctask, retrieve_classifytask, \
                           retrieve_pagetask
from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from functools import reduce

def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


class CCTaskViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = CCTask.objects.all()
    serializer_class = CCTaskSerializer

    @detail_route(methods=['post'], url_path='done')
    @transaction.atomic
    def tobe_done(self, request, pk):
        task = CCTask.objects.get(pk=pk)
        can_write_fields = getattr(RectSerializer.Meta, 'can_write_fields', [])

        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        ids = [x['id'] for x in  task.rect_set]
        req_ids = [x['id'] for x in  request.data['rects']]
        if ilen(filter(lambda x: x not in ids, req_ids)) != 0:
            return Response({"status": -1,
                             "msg": u"有些字块不属于你的任务!"})
        rect_set = [dict((k,v) for (k,v) in filter(lambda x:x[0] in can_write_fields,
            rect.items())) for rect in request.data['rects']]
        rects = RectSerializer(data=rect_set, many=True)
        if rects.is_valid():
            rects.save()
            task.done()
            return Response({"status": 0,
                             "task_id": pk })

        return Response({ "status": -1,
                "msg": rects.errors
            })


    @detail_route(methods=['post'], url_path='abandon')
    def abandon(self, request, pk):
        task = CCTask.objects.get(pk=pk)
        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        task.abandon()
        return Response({
            "status": 0,
            "task_id": pk
        })

    @list_route( methods=['get'], url_path='obtain')
    def obtain(self, request):
        staff = request.user
        task = retrieve_cctask(staff)
        if not task:
            return Response({"status": -1,
                             "msg": "All tasks has been done!"})
        return Response({"status": 0,
                        "rects": task.rect_set,
                        "task_id": task.pk})


class ClassifyTaskViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = ClassifyTask.objects.all()
    serializer_class = ClassifyTaskSerializer

    @detail_route(methods=['post'], url_path='done')
    @transaction.atomic
    def tobe_done(self, request, pk):
        task = ClassifyTask.objects.get(pk=pk)
        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        for rect in request.data['rects']:
            rect_id = rect['id']
            rect.pop('cncode', None)
            if rect_id is None:
                Rect.objects.create(**rect)
            else:
                Rect.objects.filter(pk=rect_id).update(**rect)
        task.done()
        return Response({
            "status": 0,
            "task_id": pk
        })


    @detail_route(methods=['post'], url_path='abandon')
    def abandon(self, request, pk):
        task = ClassifyTask.objects.get(pk=pk)
        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        task.abandon()
        return Response({
            "status": 0,
            "task_id": pk
        })

    @list_route(methods=['get'], url_path='obtain')
    def obtain(self, request):
        staff = request.user
        task = retrieve_classifytask(staff)
        if not task:
            return Response({"status": -1,
                             "msg": "All tasks has been done!"})
        return Response({
                        "rects": task.rect_set,
                        "task_id": task.id})


class PageTaskViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = PageTask.objects.all()
    serializer_class = PageTaskSerializer


    @list_route(methods=['get'], url_path='obtain')
    def obtain(self, request):
        staff = request.user
        task = retrieve_pagetask(staff)
        if not task:
            return Response({"status": -1,
                             "msg": "All tasks has been done!"})
        pages = PageRect.objects.filter(id__in=task.pages).select_related('page')
        return Response({
                        "pages": PageRectSerializer(pages, many=True).data,
                        "task_id": task.id})


    @detail_route(methods=['post'], url_path='abandon')
    def abandon(self, request, pk):
        task = PageTask.objects.get(pk=pk)
        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        task.abandon()
        return Response({
            "status": 0,
            "task_id": pk
        })


    @detail_route(methods=['post'], url_path='done')
    @transaction.atomic
    def tobe_done(self, request, pk):
        task = PageTask.objects.get(pk=pk)
        if (task.owner != request.user):
            return Response({"status": -1,
                             "msg": "No Permission!"})
        for page in request.data['pages']:
            page_id = page['id']
            page.pop('s3_uri', None)
            page_rect = PageRect.objects.filter(pk=page_id).first()
            if page_rect:
                page_rect.json_rects = page.pop('json_rects', None)
                page_rect.op = OpStatus.CHANGED
                page_rect.save()
        task.done()
        return Response({
            "status": 0,
            "task_id": pk
        })