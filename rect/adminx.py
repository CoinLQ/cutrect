# -*- coding: UTF-8 -*-
from __future__ import absolute_import
import xadmin
from xadmin import views
from .models import *
from xadmin.layout import Main, TabHolder, Tab, Fieldset, Row, Col, AppendedText, Side
from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction
from xadmin.filters import MultiSelectFieldListFilter
from django.db.models import Q

from django.utils.translation import ugettext as _
from django.db.models import Q

from .forms import ScheduleModelForm

@xadmin.sites.register(views.website.IndexView)
class MainDashboard(object):
    widgets = [
        [
            {"type": "html", "title": u"大藏经", "content": "<h3> 欢迎来到龙泉大藏经切分管理平台 </h3><p>加入我们，@longquan</p>"},
        ],
        [
            {"type": "list", "model": "rect.Schedule", "params": {"o": "-created_at"}},
            {"type": "addform", "model": Schedule}
        ]
    ]

'''
全局配置
'''

@xadmin.sites.register(views.BaseAdminView)
class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


@xadmin.sites.register(views.CommAdminView)
class GlobalSetting(object):
    global_search_models = [Schedule]
    global_models_icon = {
        PageRect: "fa fa-pagelines", Schedule: "fa fa-laptop", #, Task: "fa fa-bars"
        Tripitaka: "fa fa-align-justify", LQSutra: "fa fa-file-text-o", Sutra: "fa fa-file-text-o"
    }
    menu_style = 'default'  # 'accordion'


'''
基础配置
'''

@xadmin.sites.register(PageRect)
class PageRectAdmin(object):
    list_display = ("id", "page", "line_count", "column_count", "rect_set", "created_at")
    list_display_links = ("id",)
    list_filter = ("page", 'created_at')
    search_fields = ["id" ]
    date_hierarchy = 'created_at'  # 详细时间分层筛选
    relfield_style = "fk-select"
    reversion_enable = True


@xadmin.sites.register(Schedule)
class ScheduleAdmin(object):
    #form = ScheduleModelForm

    def remain_task_count(self, instance):
        count = CCTask.objects.filter(schedule=instance.id, status__in=TaskStatus.remain_status).count()
        if count > 0:
            return """<a href='/xadmin/rect/cctask/?_p_roll__id__exact=%s'>%s</a>""" % (instance.id, count)
        return count
    remain_task_count.short_description = "未完成任务"
    remain_task_count.allow_tags = True
    remain_task_count.is_column = True

    list_display = ("name",  "status", "due_at", 'created_at')
    list_display_links = ("name", "status")
    list_filter = ('status', 'due_at', 'created_at')
    search_fields = ["name" ]
    date_hierarchy = 'due_at'
    relfield_style = "fk-select"
    reversion_enable = True
    style_fields = {'reels': 'm2m_transfer'}


@xadmin.sites.register(LQSutra)
class LQSutraAdmin(object):
    list_display = ('name', 'code', 'total_reels')
    list_display_links = ('code',)

    search_fields = ('name', 'code')
    list_editable = ('total_reels',)
    list_filter = ('name', 'code')


@xadmin.sites.register(Tripitaka)
class TripitakaAdmin(object):
    list_display = ('name', 'code')
    list_display_links = ('code',)

    search_fields = ('name', 'code')
    list_editable = ('name',)
    list_filter = ('name', 'code')

@xadmin.sites.register(Sutra)
class SutraAdmin(object):
    list_display = ('name', 'code', 'total_reels')
    list_display_links = ('code',)

    search_fields = ('name', 'code')
    list_editable = ('total_reels',)
    list_filter = ('name', 'code')

@xadmin.sites.register(Schedule_Task_Statistical)
class Schedule_Task_StatisticalAdmin(object):
    list_display = ('schedule', 'amount_of_cctasks', 'completed_cctasks', 'amount_of_classifytasks',
        'completed_classifytasks', 'amount_of_absenttasks', 'completed_absenttasks', 'amount_of_pptasks',
        'completed_pptasks', 'amount_of_vdeltasks', 'completed_vdeltasks', 'amount_of_reviewtasks',
        'completed_reviewtasks', 'remark', 'updated_at')
    list_display_links = ('completed_cctasks',)
    search_fields = ('schedule',)
    list_editable = ('remark',)
    list_filter = ('completed_cctasks',)


@xadmin.sites.register(Reel_Task_Statistical)
class Reel_Task_StatisticalAdmin(object):
    list_display = ('schedule', 'reel', 'amount_of_cctasks', 'completed_cctasks',
        'amount_of_absenttasks', 'completed_absenttasks', 'amount_of_pptasks',
        'completed_pptasks', 'updated_at')
    list_display_links = ('completed_cctasks', 'reel')
    search_fields = ('schedule', 'reel')
    list_filter = ('completed_cctasks',)


# @xadmin.sites.register(Task)
# class TaskAdmin(object):
#     list_display = ("number", "schedule", "ttype", "status", "date", "rect_set", "data")
#     list_display_links = ("number", 'status')
#     list_filter = ('schedule', 'type', 'status', 'date')
#     search_fields = ["number" ]
#     date_hierarchy = 'date'
#     relfield_style = "fk-select"
#     reversion_enable = True


# @xadmin.sites.register(Patch)
# class PatchAdmin(object):
#     list_display = ('id', 'task', 'schedule', 'ch', 'cc', 'wcc', 'ts', 'ctxt', 'date', 'x', 'y', 'w', 'h', 'char_no', 'line_no', 'rect')
#     list_display_links = ("id",)
#     list_filter = ('task', 'schedule', 'cc', 'wcc', 'date' )
#     search_fields = ["id", 'ch', 'ts' ]
#     date_hierarchy = 'date'
#     relfield_style = "fk-select"
#     reversion_enable = True


# @xadmin.sites.register(AccessRecord)
# class AccessRecordAdmin(object):
#     def avg_count(self, instance):
#         return int(instance.view_count / instance.user_count)
#
#     avg_count.short_description = "Avg Count"
#     avg_count.allow_tags = True
#     avg_count.is_column = True
#
#     list_display = ("date", "user_count", "view_count", "avg_count")
#     list_display_links = ("date",)
#
#     list_filter = ["date", "user_count", "view_count"]
#     actions = None
#     aggregate_fields = {"user_count": "sum", "view_count": "sum"}
#
#     refresh_times = (3, 5, 10)
#     data_charts = {
#         "user_count": {'title': u"User Report", "x-field": "date", "y-field": ("user_count", "view_count"),
#                        "order": ('date',)},
#         "avg_count": {'title': u"Avg Report", "x-field": "date", "y-field": ('avg_count',), "order": ('date',)},
#         "per_month": {'title': u"Monthly Users", "x-field": "_chart_month", "y-field": ("user_count",),
#                       "option": {
#                           "series": {"bars": {"align": "center", "barWidth": 0.8, 'show': True}},
#                           "xaxis": {"aggregate": "sum", "mode": "categories"},
#                       },
#                       },
#     }
#
#     def _chart_month(self, obj):
#         return obj.date.strftime("%B")