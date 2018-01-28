# Create your views here.
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, views

from rect.serializers import *
from rect.forms import ScheduleForm
from utils.mixin_utils import LoginRequiredMixin



#class CreateScheduleView(LoginRequiredMixin, View):
# class CreateScheduleView(View):
#
#     @csrf_exempt
#     def post(self, request):
#         scheduleForm = ScheduleForm(request.POST)
#
#         if scheduleForm.is_valid():
#             # 创建计划信息.
#             schedule = scheduleForm.save()
#             ss = ScheduleSerializer(schedule)
#             data = JSONRenderer().render(ss.data)
#
#             res = {'code': 0, 'msg': 'success'}
#             # todo 1223 异步去分配任务.
#         else:
#             res = {'code': -1, 'msg': '请求数据错误', 'data': scheduleForm.errors}
#         return HttpResponse(json.dumps(res), content_type='application/json')
#
# # class CreateScheduleView(LoginRequiredMixin, View):
# class UploadBatchView(View):
#
#     @csrf_exempt
#     def post(self, request):
#         batchModelForm = BatchModelForm(request.POST)
#
#         if batchModelForm.is_valid():
#             # 创建计划信息.
#             batch = batchModelForm.save()
#             bs = BatchSerializer(batch)
#             data = JSONRenderer().render(bs.data)
#
#             res = {'code': 0, 'msg': 'success'}
#             # todo 1223 异步去分配任务.
#         else:
#             res = {'code': -1, 'msg': '请求数据错误', 'data': batchModelForm.errors}
#         return HttpResponse(json.dumps(res), content_type='application/json')
#
#
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, viewsets, views
from rest_framework.renderers import JSONRenderer

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import os

from rect.serializers import *
from rect.forms import ScheduleForm, BatchModelForm, OCRDataModelForm
from utils.mixin_utils import LoginRequiredMixin


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


class CCTaskViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = CCTask.objects.all()
    serializer_class = CCTaskSerializer


class ClassifyTaskViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = ClassifyTask.objects.all()
    serializer_class = ClassifyTaskSerializer


class PageTaskViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = PageTask.objects.all()
    serializer_class = PageTaskSerializer


class TestOCRViewSet(viewsets.ModelViewSet):
    queryset = OCRData.objects.all()
    serializer_class = OCRDataSerializer

    print('nice')


# class CreateScheduleView(LoginRequiredMixin, View):
class CreateScheduleView(View):

    @csrf_exempt
    def post(self, request):
        scheduleForm = ScheduleForm(request.POST)

        if scheduleForm.is_valid():
            # 创建计划信息.
            schedule = scheduleForm.save()
            ss = ScheduleSerializer(schedule)
            data = JSONRenderer().render(ss.data)

            res = {'code': 0, 'msg': 'success'}
            # todo 1223 异步去分配任务.
        else:
            res = {'code': -1, 'msg': '请求数据错误', 'data': scheduleForm.errors}
        return HttpResponse(json.dumps(res), content_type='application/json')


# class CreateScheduleView(LoginRequiredMixin, View):
class UploadBatchView(View):

    @csrf_exempt
    def post(self, request):
        batchModelForm = BatchModelForm(request.POST)

        if batchModelForm.is_valid():
            # 创建计划信息.
            batch = batchModelForm.save()
            bs = BatchSerializer(batch)
            data = JSONRenderer().render(bs.data)

            res = {'code': 0, 'msg': 'success'}
            # todo 1223 异步去分配任务.
        else:
            res = {'code': -1, 'msg': '请求数据错误', 'data': batchModelForm.errors}
        return HttpResponse(json.dumps(res), content_type='application/json')

        # class PatchViewSet(viewsets.ModelViewSet):

#     queryset = Patch.objects.all()
#     serializer_class = PatchSerializer


# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     查看、编辑用户的界面
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#
#
# class GroupViewSet(viewsets.ReadOnlyModelViewSet):
#     """
#     查看、编辑组的界面
#     """
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer


@api_view(['POST', 'GET'])
def add_ocr_tab(request, *args):
    dict = {}
    from rect import get_ocr_text
    import urllib
    from base64 import b64encode
    if request.method == 'GET':
        res = request.GET
        return Response({
            'test': res,
        })

    elif request.method == 'POST':
        jsonData = {}
        requestJson = json.loads(request.body.decode('utf-8'))

        imagePath = None
        imageData = None
        status = -1
        msg = 'error'
        data = None
        if 'img_url' in requestJson:
            imagePath = requestJson['img_url']
        if 'img_data' in requestJson:
            imageData = requestJson['img_data']
        if imageData != None and len(imageData) > 0:
            picPath = imageData
            imgBase64 = picPath
            respData = get_ocr_text.testAPI(imgBase64)

            id = None
            if 'code' in respData:
                status = respData['code']
            if 'message' in respData:
                msg = respData['message']
            if 'data' in respData:
                # data = respData['data']
                if 'id' in requestJson:
                    id = requestJson['id']
                rects = get_ocr_text.jsonToNewJson(respData)
                # if 'rect' in requestJson:
                #     rect = requestJson['rect']
                #     if len(rect) >= 4:
                #         x1 = rect[0]
                #         y1 = rect[1]
                #         x2 = rect[2]
                #         y2 = rect[3]
                #         #修改坐标
                #         for x in range(len(rects)):
                #             rectDic = rects[x]
                #             rectDic['x1'] = x1
                #             rectDic['y1'] = y1
                #             rectDic['x2'] = x2
                #             rectDic['y2'] = y2
                #             rects[x] = rectDic
                dataDic = {'id': id, 'rects': rects}
                data = str(dataDic)
            jsonData = {'status': status, 'msg': msg, 'data': data}
        elif imagePath != None:
            picPath = imagePath
            image = urllib.request.urlopen(picPath).read()
            imgBase64 = b64encode(image)
            respData = get_ocr_text.testAPI(imgBase64)
            status = -1
            msg = 'error'
            data = None
            id = None
            if 'code' in respData:
                status = respData['code']
                if int(status) == 0:
                    status = 200 + abs(status)
                elif int(status) < 0:
                    status = 400 + abs(status)
                else:
                    status = 500 + abs(status)
            else:
                status = 404
            if 'message' in respData:
                msg = respData['message']
            if 'data' in respData:
                # data = respData['data']
                if 'id' in requestJson:
                    id = requestJson['id']
                rects = get_ocr_text.jsonToNewJson(respData)
                # if 'rect' in requestJson:
                #     rect = requestJson['rect']
                #     if len(rect) >= 4:
                #         x1 = rect[0]
                #         y1 = rect[1]
                #         x2 = rect[2]
                #         y2 = rect[3]
                #         #修改坐标
                #         for x in range(len(rects)):
                #             rectDic = rects[x]
                #             rectDic['x1'] = x1
                #             rectDic['y1'] = y1
                #             rectDic['x2'] = x2
                #             rectDic['y2'] = y2
                #             rects[x] = rectDic
                dataDic = {'id': id, 'rects': rects}
                data = str(dataDic)
            jsonData = {'status': status, 'msg': msg, 'data': data}

        return Response(jsonData)
