from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, viewsets, views
from rest_framework.renderers import JSONRenderer

import json


from rect.serializers import *
from rect.forms import ScheduleForm
from utils.mixin_utils import LoginRequiredMixin

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



#class CreateScheduleView(LoginRequiredMixin, View):
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