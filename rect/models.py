# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid

import db_file_storage
from db_file_storage.storage import DatabaseFileStorage
db_storage = DatabaseFileStorage()

class ORGGroup(object):
    ALI = 0
    BAIDU = 1
    HN = 2
    IDS = (
        (ALI, u'阿里'),
        (BAIDU, u'百度'),
        (HN, u'华南理工'),
    )


class SliceType(object):
    PREPAGE = 1
    CC = 2
    CLUSTER = 3
    CHOICES = (
        (CC, u'置信度'),
        (PREPAGE, u'顺序校对'),
        (CLUSTER, u'聚类'),
    )


class ScheduleStatus:
    NOT_ACTIVE = 0
    ACTIVE = 1
    EXPIRED = 2
    DISCARD = 3
    COMPLETED = 4
    CHOICES = (
        (NOT_ACTIVE, u'未激活'),
        (ACTIVE, u'已激活'),
        (EXPIRED, u'已过期'),
        (DISCARD, u'已作废'),
        (COMPLETED, u'已完成'),
    )


class TaskStatus:
    NOT_GOT = -1
    GOT_NO_START = 0
    HANDLING = 1
    EXPIRED = 2
    DISCARD = 3
    COMPLETED = 4
    CHOICES = (
        (NOT_GOT, u'未领取'),
        (GOT_NO_START, u'已领取'),
        (HANDLING, u'处理中'),
        (EXPIRED, u'已过期'),
        (DISCARD, u'已作废'),
        (COMPLETED, u'已完成'),
    )
    #未完成状态.
    remain_status = [NOT_GOT, GOT_NO_START, HANDLING]


class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, verbose_name=u'批次名')
    series = models.CharField(max_length=64, verbose_name=u'藏经版本名')
    org = models.PositiveSmallIntegerField(
        choices=ORGGroup.IDS,
        default=ORGGroup.ALI,
        verbose_name=u'组织名称',
    )
    upload = models.FileField(null=True, upload_to='', verbose_name=u'上传批次数据')
    submit_date = models.DateField(null=True, blank=True, verbose_name=u'提交时间')
    remark = models.TextField(null=True, blank=True, verbose_name=u'备注')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"批次"
        verbose_name_plural = u"批次管理"
        ordering = ('submit_date', 'name')


class PageRect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.CharField(max_length=64, null=True, verbose_name=u'关联页ID')
    batch = models.ForeignKey(Batch, null=True, blank=True, related_name='pagerects', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'批次') #todo 1204 后续考虑用级联删除.
    line_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大行数')
    column_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大列数')
    rect_set = models.TextField(blank=True, null=True, verbose_name=u'切字块数据集')
    create_date = models.DateField(null=True, blank=True, verbose_name=u'创建时间')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = u"源-切分页"
        verbose_name_plural = u"源-切分页管理"
        ordering = ('create_date',)


# class AbstractRect(object):
#     x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
#     y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
#     w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1,
#                                          validators=[MinValueValidator(1), MaxValueValidator(300)])
#     h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1,
#                                          validators=[MinValueValidator(1), MaxValueValidator(300)])
#     ln = models.PositiveSmallIntegerField(verbose_name=u'行号', default=0)  # 旋转90度观想，行列概念
#     cn = models.PositiveSmallIntegerField(verbose_name=u'列号', default=0)
#     cc = models.FloatField(verbose_name=u'置信度', default=1, db_index=True)
#     word = models.CharField(verbose_name=u'汉字', max_length=4, default='', db_index=True)
#     wcc = models.FloatField(verbose_name=u'文字置信度', default=1, db_index=True)
#     ts = models.CharField(verbose_name=u'标字', max_length=4, default='', db_index=True)
#     ctxt = models.CharField(verbose_name=u'标字', max_length=12, default='') #todo 1205 考虑是否必要.

class RectType(object):
    NORMAL = 256
    CHOICES = (
        (NORMAL, u'正常'),
    )

class Rect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #type = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'类型', default=0) #todo 1015 有什么用途了
    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1,
                                         validators=[MinValueValidator(1), MaxValueValidator(300)])
    h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1,
                                         validators=[MinValueValidator(1), MaxValueValidator(300)])
    ln = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 旋转90度观想，行列概念
    cn = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'列号', default=0)
    cc = models.FloatField(null=True, blank=True, verbose_name=u'置信度', default=1, db_index=True)
    word = models.CharField(null=True, blank=True, verbose_name=u'汉字', max_length=4, default='', db_index=True)
    wcc = models.FloatField(null=True, blank=True, verbose_name=u'文字置信度', default=1, db_index=True)
    ts = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=4, default='', db_index=True)
    ctxt = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=12, default='') #todo 1205 考虑是否必要.

    page_rect = models.ForeignKey(PageRect, null=True, blank=True, related_name='rects', on_delete=models.SET_NULL,
                                  verbose_name=u'源-切分页') #todo 1204 后续考虑用级联删除.
    # batch = models.ForeignKey(Batch, null=True, blank=True, related_name='rects', on_delete=models.SET_NULL,
    #                           db_index=True, verbose_name=u'批次')  #todo 1204 后续考虑用级联删除.
    inset = models.FileField(null=True, blank=True, help_text=u'嵌入临时截图',
                             upload_to='core.DBPicture/bytes/filename/mimetype',
                             storage=db_storage)
    s3_inset = models.FileField(blank=True, null=True, verbose_name=u's3地址', upload_to='tripitaka/hans',
                                storage='storages.backends.s3boto.S3BotoStorage')

    def __str__(self):
        return self.word

    @staticmethod
    def generate(dict={}):
        getVal = lambda key, default=None: dict[key] if key in dict and dict[key] else default
        rect = Rect()
        rect.x = getVal('x')
        rect.y = getVal('y')
        rect.w = getVal('w')
        rect.h = getVal('h')
        rect.ln = getVal('ln')
        rect.cn = getVal('cn')
        rect.cc = getVal('cc')
        rect.wcc = getVal('wcc')
        rect.word = getVal('word')
        return rect

    class Meta:
        verbose_name = u"源-切字块"
        verbose_name_plural = u"源-切字块管理"
        ordering = ('word',)


class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, null=True, blank=True, related_name='schedules', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'批次')
    name = models.CharField(max_length=64, verbose_name=u'切分计划名')
    type = models.PositiveSmallIntegerField(
        db_index=True,
        choices=SliceType.CHOICES,
        default=SliceType.PREPAGE,
        verbose_name=u'切分方式',
    )
    desc = models.TextField(null=True, blank=True, verbose_name=u'计划格式化描述')
    user_group = models.CharField(max_length=64, null=True, blank=True, db_index=True, verbose_name=u'分配组') #todo 1204 需要跟用户系统组对接.
    status = models.PositiveSmallIntegerField(
        db_index=True,
        choices=ScheduleStatus.CHOICES,
        default=ScheduleStatus.ACTIVE,
        verbose_name=u'计划状态',
    )
    end_date = models.DateField(null=True, blank=True, db_index=True, verbose_name=u'截止日期')
    create_date = models.DateField(null=True, blank=True, verbose_name=u'创建日期')
    remark = models.TextField(null=True, blank=True, verbose_name=u'备注')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u"切分计划"
        verbose_name_plural = u"切分计划管理"
        ordering = ('end_date', "name", "status")


class Task(models.Model):
    '''
    切分校对计划的任务实例
    估计划激活后, 即后台自动据校对类型分配任务列表.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(max_length=64, verbose_name='任务编号')
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='tasks', on_delete=models.SET_NULL,
                                 db_index=True, verbose_name=u'切分计划') #todo 1205 后续考虑级联删除.
    type = models.PositiveSmallIntegerField(
        db_index=True,
        choices=SliceType.CHOICES,
        default=SliceType.PREPAGE,
        verbose_name=u'切分方式',
    )
    desc = models.TextField(null=True, blank=True, verbose_name=u'任务格式化描述')
    status = models.PositiveSmallIntegerField(
        db_index=True,
        choices=TaskStatus.CHOICES,
        default=TaskStatus.NOT_GOT,
        verbose_name=u'任务状态',
    )
    date = models.DateField(null=True, verbose_name=u'最近处理时间')
    rect_set = models.TextField(null=True, verbose_name=u'页切片数据') #todo 1215 可做为关联的patch集合的序列化结果.
    data = models.TextField(null=True, verbose_name=u'附加数据')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = u"切分任务"
        verbose_name_plural = u"切分任务管理"
        ordering = ('schedule', "number", "status")


class Patch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1,
                                         validators=[MinValueValidator(1), MaxValueValidator(300)])
    h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1,
                                         validators=[MinValueValidator(1), MaxValueValidator(300)])
    ln = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 旋转90度观想，行列概念
    cn = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'列号', default=0)  # todo ln cn, 考虑patch提交后不参与其中, 只作补充Rect, 固不需要这两个字段了.
    cc = models.FloatField(null=True, blank=True, verbose_name=u'置信度', default=1, db_index=True) #todo 1215 可以删掉, 因为patch是人工操作
    word = models.CharField(null=True, blank=True, verbose_name=u'汉字', max_length=4, default='', db_index=True)
    wcc = models.FloatField(null=True, blank=True, verbose_name=u'文字置信度', default=1, db_index=True) #todo 1215 可以删掉, 因为patch是人工操作
    ts = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=4, default='', db_index=True)
    ctxt = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=12, default='') #todo 1205 考虑是否必要.

    rect = models.ForeignKey(Rect, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
                             verbose_name=u'源-切字块数据')  #一个批次可能存在多个切分计划, 所以有多个批次中的多个切块对应着这个批次的某个切块.
    task = models.ForeignKey(Task, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
                             verbose_name=u'切分任务') #todo 1205 后续考虑级联删除.
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
                                 db_index=True, verbose_name=u'切分计划') #todo 1205 后续考虑级联删除.
    date = models.DateField(null=True, blank=True, verbose_name=u'最近处理时间')

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = u"Patch"
        verbose_name_plural = u"Patch管理"
        ordering = ('schedule', "task", "word")


class AccessRecord(models.Model):
    date = models.DateField()
    user_count = models.IntegerField()
    view_count = models.IntegerField()

    class Meta:
        verbose_name = u"访问记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s Access Record" % self.date.strftime('%Y-%m-%d')





