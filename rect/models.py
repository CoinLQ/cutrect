# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
from db_file_storage.storage import DatabaseFileStorage
from jwt_auth.models import Staff
from django.utils.timezone import localtime, now
from functools import wraps
import json


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
    PPAGE = 1
    CC = 2
    CLASSIFY = 3
    CHECK = 4
    CHOICES = (
        (CC, u'置信度'),
        (PPAGE, u'顺序校对'),
        (CLASSIFY, u'聚类'),
        (CHECK, u'差缺补漏'),
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
    NOT_GOT = 0
    EXPIRED = 1
    ABANDON = 2
    HANDLING = 4
    COMPLETED = 5
    DISCARD = 6

    CHOICES = (
        (NOT_GOT, u'未领取'),
        (EXPIRED, u'已过期'),
        (ABANDON, u'已放弃'),
        (HANDLING, u'处理中'),
        (COMPLETED, u'已完成'),
        (DISCARD, u'已作废'),
    )
    #未完成状态.
    remain_status = [NOT_GOT, EXPIRED, ABANDON, HANDLING]

class PriorityLevel:
    LOW = 1
    MIDDLE = 3
    HIGH = 5
    HIGHEST = 7

    CHOICES = (
        (LOW, u'低'),
        (MIDDLE, u'中'),
        (HIGH, u'高'),
        (HIGHEST, u'最高'),
    )

class OpStatus(object):
    NORMAL = 1
    CHANGED = 2
    DELETED = 3
    RECOG = 4
    COLLATE = 5
    CHOICES = (
        (NORMAL, u'正常'),
        (CHANGED, u'被更改'),
        (DELETED, u'被删除'),
        (RECOG, u'文字识别'),
        (COLLATE, u'文字校对')
    )

class OPage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, db_index=True, unique=True, verbose_name=u'原始页编码')
    s3_inset = models.FileField(max_length=256, blank=True, null=True, verbose_name=u's3地址', upload_to='tripitaka/hans',
                                storage='storages.backends.s3boto.S3BotoStorage')

    class Meta:
        verbose_name = u"原始页"
        verbose_name_plural = u"原始页管理"
        ordering = ('code', )


class OColumn(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opage = models.ForeignKey(OPage, related_name='ocolumns', on_delete=models.CASCADE,
                              db_index=True, verbose_name=u'原始页')
    code = models.CharField(max_length=64, db_index=True, unique=True, verbose_name=u'页的切列编码')
    location = models.CharField(max_length=64, null=True, verbose_name='位置坐标参数')
    s3_inset = models.FileField(max_length=256, blank=True, null=True, verbose_name=u's3地址', upload_to='tripitaka/hans',
                                storage='storages.backends.s3boto.S3BotoStorage')

    class Meta:
        verbose_name = u"原始页"
        verbose_name_plural = u"原始页管理"
        ordering = ('code', )

    @property
    def s3_uri(self):
        return self.s3_inset.name

    @property
    def x(self):
        n = self.location.strip().split(',')[0] or 0
        return n

    @property
    def y(self):
        try:
            n = self.location.strip().split(',')[1]
        except:
            n = 0
        return n


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
    page = models.ForeignKey(OPage, null=True, blank=True, related_name='pagerects', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'关联源页信息')
    op = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'操作类型', default=OpStatus.NORMAL)
    code = models.CharField(max_length=64, null=True, verbose_name=u'关联源页CODE') # Eg. GLZ_K1000_S0001_V0001_P0001
    batch = models.ForeignKey(Batch, null=True, blank=True, related_name='pagerects', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'批次')  # 批次删除，暂不删除切分数据
    line_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大行数')
    column_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大列数')
    rect_set = models.TextField(blank=True, null=True, verbose_name=u'切字块JSON数据集')
    create_date = models.DateField(null=True, blank=True, verbose_name=u'创建时间')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = u"源页切分集"
        verbose_name_plural = u"源页切分集管理"
        ordering = ('create_date',)

    @property
    def s3_uri(self):
        return self.page.s3_inset.name

    @property
    def json_rects(self):
        return json.loads(self.rect_set)

    @json_rects.setter
    def json_rects(self, value):
        self.rect_set = json.dumps(value, ensure_ascii=False)



class Rect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    op = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'操作类型', default=OpStatus.NORMAL)
    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1) #, validators=[MinValueValidator(1), MaxValueValidator(300)])
    h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1) #, validators=[MinValueValidator(1), MaxValueValidator(300)])
    ln = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 旋转90度观想，行列概念
    cn = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'列号', default=0)
    cc = models.FloatField(null=True, blank=True, verbose_name=u'切分置信度', default=1, db_index=True)
    word = models.CharField(null=True, blank=True, verbose_name=u'汉字', max_length=4, default='', db_index=True)
    wcc = models.FloatField(null=True, blank=True, verbose_name=u'文字置信度', default=1, db_index=True)
    ts = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=4, default='', db_index=True)
    #ctxt = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=12, default='') #todo 1205 考虑是否必要.

    batch = models.ForeignKey(Batch, null=True, related_name='rects', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'批次')
    page_rect = models.ForeignKey(PageRect, null=True, blank=True, related_name='rects', on_delete=models.SET_NULL,
                                  verbose_name=u'源页切分集') # 数据重要不级联删除，使用业务逻辑过滤删除.
    s3_inset = models.FileField(max_length=256, blank=True, null=True, verbose_name=u's3地址', upload_to='tripitaka/hans',
                                  storage='storages.backends.s3boto.S3BotoStorage')
    pcode = models.CharField(max_length=64, null=True, verbose_name=u'关联源页CODE')

    def __str__(self):
        return self.word

    @property
    def cncode(self):
        return "{0}_L{1:02}".format(self.pcode, self.cn)

    @property
    def rectcode(self):
        return "{0}_Z{1:02}".format(self.cncode, self.ln)

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
        ordering = ('-cc',)


class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, null=True, related_name='schedules', on_delete=models.SET_NULL,
                              db_index=True, verbose_name=u'批次')
    name = models.CharField(max_length=64, verbose_name=u'切分计划名')
    type = models.PositiveSmallIntegerField(
        db_index=True,
        choices=SliceType.CHOICES,
        default=SliceType.PPAGE,
        verbose_name=u'切分方式',
    )
    desc = models.CharField(max_length=256, null=True, blank=True, verbose_name=u'计划格式化描述')
    status = models.PositiveSmallIntegerField(
        db_index=True,
        null=True,
        blank=True,
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


def activity_log(func):
    @wraps(func)
    def tmp(*args, **kwargs):
        result = func(*args, **kwargs)
        self = args[0]
        ActivityLog.objects.create(user=self.owner, object_pk=self.pk,
                                    object_type=type(self).__name__,
                                    action=func.__name__)
        return result
    return tmp



class Task(models.Model):
    '''
    切分校对计划的任务实例
    估计划激活后, 即后台自动据校对类型分配任务列表.
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number = models.CharField(null=True, blank=True, max_length=64, verbose_name='任务编号')
    ttype = models.PositiveSmallIntegerField(
        db_index=True,
        choices=SliceType.CHOICES,
        default=SliceType.PPAGE,
        verbose_name=u'切分方式',
    )
    desc = models.TextField(null=True, blank=True, verbose_name=u'任务格式化描述')
    status = models.PositiveSmallIntegerField(
        db_index=True,
        choices=TaskStatus.CHOICES,
        default=TaskStatus.NOT_GOT,
        verbose_name=u'任务状态',
    )
    priority = models.PositiveSmallIntegerField(
        choices=PriorityLevel.CHOICES,
        default=PriorityLevel.MIDDLE,
        verbose_name=u'任务状态',
    )
    update_date = models.DateField(null=True, verbose_name=u'最近处理时间')

    # def __str__(self):
    #     return self.number

    @classmethod
    def serialize_set(cls, dataset):
        return ";".join(dataset)

    @activity_log
    def done(self):
        self.status = TaskStatus.COMPLETED
        return self.save(update_fields=["status"])

    @activity_log
    def abandon(self):
        self.status = TaskStatus.ABANDON
        return self.save(update_fields=["status"])

    @activity_log
    def expire(self):
        self.status = TaskStatus.EXPIRED
        return self.save(update_fields=["status"])

    @activity_log
    def obtain(self, user):
        self.update_date = localtime(now()).date()
        self.status = TaskStatus.HANDLING
        self.owner = user
        self.save()

    class Meta:
        abstract = True
        verbose_name = u"切分任务"
        verbose_name_plural = u"切分任务管理"
        ordering = ("priority", "status")
        indexes = [
            models.Index(fields=['priority', 'status']),
        ]


class CCTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='cc_tasks', on_delete=models.SET_NULL,
                                 db_index=True, verbose_name=u'切分计划')  # todo 1205 后续考虑级联删除.
    count = models.IntegerField("任务字块数")
    cc_threshold = models.FloatField("最高置信度")
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='cc_tasks')
    rect_set = models.TextField(null=True, verbose_name=u'字块集') # [rect_id, rect_id]

    @property
    def rects(self):
        return self.rect_set.split(';')


class ClassifyTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='classify_tasks', on_delete=models.SET_NULL,
                                 db_index=True, verbose_name=u'切分计划')  # todo 1205 后续考虑级联删除.
    count = models.IntegerField("任务字块数")
    char_set = models.TextField(null=True, blank=True, verbose_name=u'字符集') # [ ‘人’, ‘无’]
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='classify_tasks')
    rect_set = models.TextField(null=True, verbose_name=u'字块集') # [rect_id, rect_id]

    @property
    def rects(self):
        return self.rect_set.split(';')

class PageTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='page_tasks', on_delete=models.SET_NULL,
                                 db_index=True, verbose_name=u'切分计划')  # todo 1205 后续考虑级联删除.
    count = models.IntegerField("页的数量")
    page_set = models.TextField(null=True, verbose_name=u'页的集合') # [page_id, page_id]
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='page_tasks')

    @property
    def pages(self):
        return self.page_set.split(';')



# class Patch(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
#     y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
#     w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1,
#                                          validators=[MinValueValidator(1), MaxValueValidator(300)])
#     h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1,
#                                          validators=[MinValueValidator(1), MaxValueValidator(300)])
#     ln = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 旋转90度观想，行列概念
#     cn = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'列号', default=0)  # todo ln cn, 考虑patch提交后不参与其中, 只作补充Rect, 固不需要这两个字段了.
#     cc = models.FloatField(null=True, blank=True, verbose_name=u'置信度', default=1, db_index=True) #todo 1215 可以删掉, 因为patch是人工操作
#     word = models.CharField(null=True, blank=True, verbose_name=u'汉字', max_length=4, default='', db_index=True)
#     wcc = models.FloatField(null=True, blank=True, verbose_name=u'文字置信度', default=1, db_index=True) #todo 1215 可以删掉, 因为patch是人工操作
#     ts = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=4, default='', db_index=True)
#     ctxt = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=12, default='') #todo 1205 考虑是否必要.

#     rect = models.ForeignKey(Rect, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
#                              verbose_name=u'源-切字块数据')  #一个批次可能存在多个切分计划, 所以有多个批次中的多个切块对应着这个批次的某个切块.
#     task = models.ForeignKey(Task, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
#                              verbose_name=u'切分任务') #todo 1205 后续考虑级联删除.
#     schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='patches', on_delete=models.SET_NULL,
#                                  db_index=True, verbose_name=u'切分计划') #todo 1205 后续考虑级联删除.
#     date = models.DateField(null=True, blank=True, verbose_name=u'最近处理时间')

#     def __str__(self):
#         return self.word

#     class Meta:
#         verbose_name = u"Patch"
#         verbose_name_plural = u"Patch管理"
#         ordering = ('schedule', "task", "word")


class ActivityLog(models.Model):
    user = models.ForeignKey(Staff, related_name='activities')
    log = models.CharField(verbose_name=u'记录', max_length=128, default='')
    object_type = models.CharField(verbose_name=u'对象类型', max_length=32)
    object_pk = models.CharField(verbose_name=u'对象主键', max_length=64)
    action = models.CharField(verbose_name=u'行为', max_length=16)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def log_message(self):
        return "User:%s %s to %s(%s) at %s" % (self.user.id,
                                               self.action, self.object_type,
                                               self.object_pk, self.created_at)

# class AccessRecord(models.Model):
#     date = models.DateField()
#     user_count = models.IntegerField()
#     view_count = models.IntegerField()
#
#     class Meta:
#         verbose_name = u"访问记录"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return "%s Access Record" % self.date.strftime('%Y-%m-%d')





