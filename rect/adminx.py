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

from .forms import BatchModelForm, ScheduleModelForm

@xadmin.sites.register(views.website.IndexView)
class MainDashboard(object):
    widgets = [
        [
            {"type": "html", "title": u"大藏经", "content": "<h3> 欢迎来到龙泉大藏经切分管理平台 </h3><p>加入我们，@longquan</p>"},
            {"type": "addform", "model": Batch}
        ],
        [
            {"type": "list", "model": "rect.Schedule", "params": {"o": "-create_date"}},
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
    global_search_models = [Batch, Schedule]
    global_models_icon = {
        Batch: "fa fa-copy", PageRect: "fa fa-pagelines", Schedule: "fa fa-laptop" #, Task: "fa fa-bars"
    }
    menu_style = 'default'  # 'accordion'


# class PageResourceInline(object):
#     model = PageResource
#     extra = 1
#     style = "accordion"


'''
基础配置
'''

@xadmin.sites.register(Batch)
class BatchAdmin(object):
    form = BatchModelForm
    list_display = ("name", "series", "org", "upload", "submit_date", "remark")
    list_display_links = ("name",)
    list_filter = ('series', 'org', 'submit_date')  # 过滤器
    search_fields = ("name",)
    date_hierarchy = 'submit_date'  # 详细时间分层筛选
    relfield_style = "fk-select"
    reversion_enable = True


@xadmin.sites.register(PageRect)
class PageRectAdmin(object):
    list_display = ("id", "page", "line_count", "column_count", "rect_set", "create_date", "batch")
    list_display_links = ("id",)
    list_filter = ("page", 'create_date', 'batch')
    search_fields = ["id" ]
    date_hierarchy = 'create_date'  # 详细时间分层筛选
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

    list_display = ("name", "batch", "type", 'remain_task_count', "status", "end_date", 'create_date')
    list_display_links = ("name", "status")
    list_filter = ("batch", 'type', 'status', 'end_date', 'create_date')
    search_fields = ["name" ]
    date_hierarchy = 'end_date'
    relfield_style = "fk-select"
    reversion_enable = True


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
#     list_display = ('id', 'task', 'schedule', 'word', 'cc', 'wcc', 'ts', 'ctxt', 'date', 'x', 'y', 'w', 'h', 'ln', 'cn', 'rect')
#     list_display_links = ("id",)
#     list_filter = ('task', 'schedule', 'cc', 'wcc', 'date' )
#     search_fields = ["id", 'word', 'ts' ]
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