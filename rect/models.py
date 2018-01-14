# -*- coding: UTF-8 -*-
from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from jwt_auth.models import Staff
from django.utils.timezone import localtime, now
from functools import wraps
import json
import urllib.request
from jsonfield import JSONField
from django.db import connection, transaction
from django.db.models import Sum, Case, When, Value, Count, Avg
from django_bulk_update.manager import BulkUpdateManager
from .lib.arrange_rect import ArrangeRect
from dotmap import DotMap

def iterable(cls):
    """
    model的迭代器并输出dict，且不包含内部__,_开头的key
    """
    @wraps(cls)
    def iterfn(self):
        iters = dict((k, v) for k, v in self.__dict__.items() if not k.startswith("_"))

        for k, v in iters.items():
            yield k, v

    cls.__iter__ = iterfn
    return cls

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

class PageStatus:
    INITIAL = 0
    RECT_NOTFOUND = 1
    PARSE_FAILED = 2
    RECT_NOTREADY = 3
    CUT_PIC_NOTFOUND = 4
    COL_PIC_NOTFOUND = 5
    COL_POS_NOTFOUND = 6
    RECT_COL_NOTREADY = 7
    RECT_COL_NOTFOUND = 8
    READY = 9
    MARKED = 10

    CHOICES = (
        (INITIAL, u'初始化'),
        (RECT_NOTFOUND, u'切分数据未上传'),
        (PARSE_FAILED, u'数据解析失败'),
        (RECT_NOTREADY, u'字块数据未展开'),
        (CUT_PIC_NOTFOUND, u'图片不存在'),
        (COL_PIC_NOTFOUND, u'列图不存在'),
        (COL_POS_NOTFOUND, u'列图坐标不存在'),
        (RECT_COL_NOTREADY, u'字块对应列图未准备'),
        (RECT_COL_NOTFOUND, u'字块对应列图不存在'),
        (READY, u'已准备好'),
        (MARKED, u'已入卷标记'),
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

class ReviewResult(object):
    INITIAL = 0
    AGREE = 1
    DISAGREE = 2
    IGNORED = 3
    CHOICES = (
        (INITIAL, u'未审阅'),
        (AGREE, u'已同意'),
        (DISAGREE, u'未同意'),
        (IGNORED, u'被略过'),
    )


class TripiMixin(object):
    def __str__(self):
        return self.name

class Node(models.Model):
    name = models.CharField(u"名称", max_length=64)
    code = models.CharField(u"节点代码", max_length=27, primary_key=True)
    parent = models.ForeignKey('self', verbose_name=u'父节点', related_name='children', null=True, blank=True)

    class Meta:
        verbose_name=u'节点'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name +":" +self.code

class LQSutra(models.Model, TripiMixin):
    code = models.CharField(verbose_name='龙泉经目编码', max_length=8, primary_key=True) #（为"LQ"+ 经序号 + 别本号）
    name = models.CharField(verbose_name='龙泉经目名称', max_length=64, blank=False)
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)

    class Meta:
        verbose_name = u"龙泉经目"
        verbose_name_plural = u"龙泉经目管理"


class Tripitaka(models.Model, TripiMixin):
    code = models.CharField(verbose_name='实体藏经版本编码', primary_key=True, max_length=4, blank=False)
    name = models.CharField(verbose_name='实体藏经名称', max_length=32, blank=False)

    class Meta:
        verbose_name = '实体藏经'
        verbose_name_plural = '实体藏经管理'


class Sutra(models.Model, TripiMixin):
    sid = models.CharField(verbose_name='实体藏经|唯一经号编码', editable=True, max_length=10, primary_key=True) # 藏经版本编码 + 5位经序号+1位别本号
    tripitaka = models.ForeignKey(Tripitaka, related_name='sutras')
    code = models.CharField(verbose_name='实体经目编码', max_length=5, blank=False)
    variant_code = models.CharField(verbose_name='别本编码', max_length=1, default='0')
    name = models.CharField(verbose_name='实体经目名称', max_length=64, blank=True)
    lqsutra = models.ForeignKey(LQSutra, verbose_name='龙泉经目编码', null=True, blank=True) #（为"LQ"+ 经序号 + 别本号）
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)

    class Meta:
        verbose_name = '实体经目'
        verbose_name_plural = '实体经目管理'

    @property
    def sutra_sn(self):
        return "%s%s%s" % (self.tripitaka_id, self.code.zfill(5), self.variant_code)

    def __str__(self):
        return self.name

class Reel(models.Model):
    rid = models.CharField(verbose_name='实体藏经卷级总编码', max_length=14, blank=False, primary_key=True)
    sutra = models.ForeignKey(Sutra, related_name='reels')
    reel_no = models.CharField(verbose_name='经卷序号编码', max_length=3, blank=False)
    ready = models.BooleanField(verbose_name='已准备好', db_index=True, default=False)
    image_ready = models.BooleanField(verbose_name='图源状态', default=False)
    image_upload = models.BooleanField(verbose_name='图片上传状态',  default=False)
    txt_ready = models.BooleanField(verbose_name='文本状态', default=False)
    cut_ready = models.BooleanField(verbose_name='切分数据状态', default=False)
    column_ready = models.BooleanField(verbose_name='切列图状态', default=False)

    class Meta:
        verbose_name = '实体藏经卷'
        verbose_name_plural = '实体藏经卷管理'

    @property
    def reel_sn(self):
        return "%sr%s" % (self.sutra_id, self.reel_no.zfill(3))

    @property
    def name(self):
        return u"第%s卷" %(self.reel_no,)

    def __str__(self):
        return self.sutra.name + self.rid

class Page(models.Model):
    pid = models.CharField(verbose_name='实体藏经页级总编码', max_length=21, blank=False, primary_key=True)
    reel = models.ForeignKey(Reel, related_name='pages')
    bar_no = models.CharField(verbose_name='实体藏经页级栏序号', max_length=1, default='0')
    vol_no = models.CharField(verbose_name='册序号编码', max_length=3, blank=False)
    page_no = models.IntegerField(verbose_name='册级页序号', default=1, blank=False)
    img_path = models.CharField(verbose_name='图片路径', max_length=128, blank=False)
    status = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'操作类型',
                                              choices=PageStatus.CHOICES, default=PageStatus.INITIAL)
    json = JSONField(default=dict)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    # s3_inset = models.FileField(max_length=256, blank=True, null=True, verbose_name=u'S3图片路径地址', upload_to='lqcharacters-images',
    #                             storage='storages.backends.s3boto.S3BotoStorage')

    def get_real_path(self):
        # FIXME: 暂时这么写可以，写死了，GEO CDN就失效了。
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path

    def down_col_pos(self):
        cut_file = self.get_real_path()[0:-3] + "col"
        opener = urllib.request.build_opener()
        try:
            response = opener.open(cut_file)
        except urllib.error.HTTPError as e:
            # 下载失败
            print(self.pid + ": col download failed")
            return
        try:
            body = response.read().decode('utf8')
            json_data = json.loads(body)
            if json_data['page_code'] == self.pid and json_data['reel_no'] == self.reel_id \
                and type(json_data['col_data'])==list :
                self.status = PageStatus.RECT_COL_NOTREADY
                self.json = json_data['col_data']
                self.save()
        except:
            print(self.pid + ": col parse failed")
            print("CONTENT:" + body)
            self.json = {"content": body}
            self.status = PageStatus.COL_POS_NOTFOUND
            self.save(update_fields=['status', 'json'])
            return

    def down_pagerect(self):
        cut_file = self.get_real_path()[0:-3] + "cut"
        opener = urllib.request.build_opener()
        try:
            response = opener.open(cut_file)
        except urllib.error.HTTPError as e:
            # 下载失败
            print(self.pid + ": rect download failed")
            self.status = PageStatus.RECT_NOTFOUND
            self.save(update_fields=['status'])
            return
        try:
            body = response.read().decode('utf8')
            json_data = json.loads(body)
            if json_data['page_code'] == self.pid and json_data['reel_no'] == self.reel_id \
                and type(json_data['char_data'])==list :
                pass
        except:
            print(self.pid + ": rect parse failed")
            print("CONTENT:" + body)
            self.json = {"content": body}
            self.status = PageStatus.PARSE_FAILED
            self.save(update_fields=['status', 'json'])
            return
        self.pagerects.all().delete()
        PageRect(page=self, reel=self.reel, line_count=0, column_count=0, rect_set=json_data['char_data']).save()
        self.status = PageStatus.RECT_NOTREADY
        self.save(update_fields=['status'])
        print(self.pid + ": pagerect saved")

    @property
    def page_sn(self):
        return "%sv%sp%04d%s" % (self.reel_id[0:-4], self.vol_no.zfill(3), self.page_no, self.bar_no)

    class Meta:
        verbose_name = '实体藏经页'
        verbose_name_plural = '实体藏经页管理'

class PageRect(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, null=True, blank=True, related_name='pagerects', on_delete=models.SET_NULL,
                             verbose_name=u'关联源页信息')
    reel = models.ForeignKey(Reel, null=True, blank=True, related_name='pagerects')
    op = models.PositiveSmallIntegerField(db_index=True, verbose_name=u'操作类型', default=OpStatus.NORMAL)
    line_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大行数') # 最大文本行号
    column_count = models.IntegerField(null=True, blank=True, verbose_name=u'最大列数') # 最大文本长度
    rect_set = JSONField(default=list, verbose_name=u'切字块JSON切分数据集')
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=u'创建时间', auto_now_add=True)
    primary = models.BooleanField(verbose_name="主切分方案", default=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = u"源页切分集"
        verbose_name_plural = u"源页切分集管理"
        ordering = ('id',)

    # @property
    # def rect_set(self):
    #     try:
    #         ret = json.loads(self._rect_set)
    #     except ValueError:
    #         return {}
    #     return ret


    # @rect_set.setter
    # def rect_set(self, val):
    #     self._rect_set = json.dumps(val)

    @property
    def s3_uri(self):
        return self.page.s3_inset.name

    def rebuild_rect(self):
        if len(self.rect_set) == 0:
            return
        cids = list(map(lambda X: X["char_id"], self.rect_set))
        Rect.objects.filter(reel=self.reel, cid__in=cids).all().delete()
        rect_list = list()
        columns, column_len = ArrangeRect.resort_rects_from_list(self.rect_set)
        for lin_n, line in columns.items():
            for col_n, _rect in enumerate(line, start=1):
                _rect['line_no'] = lin_n
                _rect['char_no'] = col_n
                rect = Rect.generate(_rect)
                rect.reel = self.reel
                rect.page_code = self.page_id
                rect_list.append(rect)
        Rect.objects.bulk_create(rect_list)
        self.line_count = max(map(lambda Y: Y.line_no, rect_list))
        self.column_count = max(map(lambda Y: Y.char_no, rect_list))
        self.save()

    @classmethod
    @transaction.atomic
    def reformat_rects(cls, page_id):
        ret = True
        rects = Rect.objects.filter(page_code=page_id).all()
        page = Page.objects.get(pk=page_id)
        if rects.count() == 0:
            return ret
        columns, column_len = ArrangeRect.resort_rects_from_qs(rects)
        rect_list = list()
        for lin_n, line in columns.items():
            for col_n, _rect in enumerate(line, start=1):
                _rect['line_no'] = lin_n
                _rect['char_no'] = col_n
                rect = Rect.generate(_rect)
                rect.id = _rect['id'] or rect.id
                rect.reel_id = page.reel_id
                rect.page_code = page_id
                try :
                    column_dict = (item for item in page.json if item["col_id"] == rect.cncode).__next__()
                    rect.column_set = column_dict
                except:
                    ret = False
                    print(rect.cncode + ': col_pos doesn\'t exist!')
                rect_list.append(rect)
        [rect.save() for rect in rect_list]
        pagerect = PageRect.objects.filter(page_id=page_id).first()
        pagerect.line_count = max(map(lambda Y: Y.line_no, rect_list))
        pagerect.column_count = max(map(lambda Y: Y.char_no, rect_list))
        pagerect.save()
        return ret

@iterable
class Rect(models.Model):
    # https://github.com/aykut/django-bulk-update
    objects = BulkUpdateManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cid = models.CharField(verbose_name=u'经字号', max_length=28, db_index=True)
    reel = models.ForeignKey(Reel, null=True, blank=True, related_name='rects')
    page_code = models.CharField(max_length=23, blank=False, verbose_name=u'关联源页CODE', db_index = True)
    column_code = models.CharField(max_length=25, null=True, verbose_name=u'关联源页切列图CODE') # auto_trigger
    column_set = JSONField(default=list, verbose_name=u'切字块所在切列JSON数据集')
    char_no = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'字号', default=0)
    line_no = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 对应图片的一列

    op = models.PositiveSmallIntegerField(verbose_name=u'操作类型', default=OpStatus.NORMAL)
    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.IntegerField(verbose_name=u'宽度', default=1)
    h = models.IntegerField(verbose_name=u'高度', default=1)

    cc = models.FloatField(null=True, blank=True, verbose_name=u'切分置信度', db_index=True, default=1)
    ch = models.CharField(null=True, blank=True, verbose_name=u'文字', max_length=2, default='', db_index=True)
    wcc = models.FloatField(null=True, blank=True, verbose_name=u'识别置信度', default=1, db_index=True)
    ts = models.CharField(null=True, blank=True, verbose_name=u'标字', max_length=2, default='')
    s3_inset = models.FileField(max_length=256, blank=True, null=True, verbose_name=u's3地址', upload_to='tripitaka/hans',
                                  storage='storages.backends.s3boto.S3BotoStorage')
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    @property
    def rect_sn(self):
        return "%s%02dn%02d" % (self.page_code, self.line_no, self.char_no)

    def __str__(self):
        return self.ch

    @property
    def serialize_set(self):
        return dict((k, v) for k, v in self.__dict__.items() if not k.startswith("_"))

    @property
    def cncode(self):
        return "%s%02d" % (self.page_code, self.line_no)

    @staticmethod
    def generate(dict={}):
        getVal = lambda key, default=None: dict[key] if key in dict and dict[key] else default
        rect = Rect()
        rect.x = getVal('id')
        rect.x = getVal('x')
        rect.y = getVal('y')
        rect.w = getVal('w')
        rect.h = getVal('h')
        rect.char_no = getVal('char_no')
        rect.line_no = getVal('line_no')
        rect.cc = getVal('cc')
        rect.wcc = getVal('wcc')
        rect.ch = getVal('char') or getVal('ch')
        rect.updated_at = getVal('updated_at')
        rect = Rect.normalize(rect)
        return rect

    @staticmethod
    def normalize(instance):
        if (instance.w < 0):
            instance.x = instance.x + instance.w
            instance.w = abs(instance.w)
        if (instance.h < 0):
            instance.y = instance.y + instance.h
            instance.h = abs(instance.h)

        if (instance.w == 0):
            instance.w = 1
        if (instance.h == 0):
            instance.h = 1
        return instance

    class Meta:
        verbose_name = u"源-切字块"
        verbose_name_plural = u"源-切字块管理"
        ordering = ('-cc',)


@receiver(pre_save, sender=Rect)
def positive_w_h_fields(sender, instance, **kwargs):
    instance = Rect.normalize(instance)

@receiver(post_save)
def create_new_node(sender, instance, created, **kwargs):
    if sender==LQSutra:
        Node(code=instance.code, name=instance.name).save()

    if sender==Sutra:
        if created:
            Node(code=instance.sutra_sn, name=instance.name, parent_id=instance.lqsutra_id).save()
        else:
            Node.objects.filter(pk=instance.sutra_sn).update(parent_id=instance.lqsutra_id)
    if sender==Reel:
        if created:
            Node(code=instance.reel_sn, name=instance.name, parent_id=instance.sutra_id).save()
        else:
            Node.objects.filter(pk=instance.reel_sn).update(parent_id=instance.sutra_id)


class Patch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reel = models.ForeignKey(Reel, null=True, blank=True, related_name='patches') # 注意：卷编码这里没有考虑余量
    op = models.PositiveSmallIntegerField(verbose_name=u'操作类型', default=OpStatus.NORMAL)
    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1)
    h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1)
    ocolumn_uri = models.CharField(verbose_name='行图片路径', max_length=128, blank=False)
    ocolumn_x = models.PositiveSmallIntegerField(verbose_name=u'行图X坐标', default=0)
    ocolumn_y = models.PositiveSmallIntegerField(verbose_name=u'行图Y坐标', default=0)
    char_no = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'字号', default=0)
    line_no = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'行号', default=0)  # 对应图片的一列
    ch = models.CharField(null=True, blank=True, verbose_name=u'文字', max_length=2, default='')
    rect_id = models.CharField(verbose_name='字块CID', max_length=128, blank=False)
    rect_x = models.PositiveSmallIntegerField(verbose_name=u'原字块X坐标', default=0)
    rect_y = models.PositiveSmallIntegerField(verbose_name=u'原字块Y坐标', default=0)
    rect_w = models.PositiveSmallIntegerField(verbose_name=u'原字块宽度', default=1)
    rect_h = models.PositiveSmallIntegerField(verbose_name=u'原字块高度', default=1)
    ts = models.CharField(null=True, blank=True, verbose_name=u'修订文字', max_length=2, default='')
    result = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'审定意见', default=ReviewResult.INITIAL)  # 1 同意 2 不同意
    modifier = models.ForeignKey(Staff, null=True, blank=True, related_name='modify_patches', verbose_name=u'修改人')
    verifier = models.ForeignKey(Staff, null=True, blank=True, related_name='verify_patches', verbose_name=u'审定人')

    submitted_at = models.DateTimeField(verbose_name='修订时间', auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=u'更新时间', auto_now=True)

    def __str__(self):
        return self.ch

    class Meta:
        verbose_name = u"Patch"
        verbose_name_plural = u"Patch管理"
        ordering = ("ch",)


class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reels = models.ManyToManyField(Reel, limit_choices_to={'ready': True}, blank=True )
    name = models.CharField(verbose_name='计划名称', max_length=64)

    cc_threshold = models.FloatField("切分置信度阈值", default=0.65, blank=True)

    # todo 设置总任务的优先级时, 子任务包的优先级凡是小于总任务优先级的都提升优先级, 高于或等于的不处理. 保持原优先级.
    priority = models.PositiveSmallIntegerField(
        choices=PriorityLevel.CHOICES,
        default=PriorityLevel.MIDDLE,
        verbose_name=u'任务计划优先级',
    )
    status = models.PositiveSmallIntegerField(
        db_index=True,
        null=True,
        blank=True,
        choices=ScheduleStatus.CHOICES,
        default=ScheduleStatus.NOT_ACTIVE,
        verbose_name=u'计划状态',
    )
    due_at = models.DateField(null=True, blank=True, verbose_name=u'截止日期')
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=u'创建日期', auto_now_add=True)
    remark = models.TextField(max_length=256, null=True, blank=True, verbose_name=u'备注')
    schedule_no = models.CharField(max_length=64, verbose_name=u'切分计划批次', default='', help_text=u'自动生成', blank=True)

    def __str__(self):
        return self.name

    def create_reels_task(self):
        # NOTICE: 实际这里不工作，多重关联这时并未创建成功。
        # 在数据库层用存储过程在关联表记录创建后，创建卷任务。
        tasks = []
        for reel in self.reels.all():
            tasks.append(Reel_Task_Statistical(schedule=self, reel=reel))
        Reel_Task_Statistical.objects.bulk_create(tasks)

    class Meta:
        verbose_name = u"切分计划"
        verbose_name_plural = u"切分计划管理"
        ordering = ('due_at', "status")


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


class Schedule_Task_Statistical(models.Model):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='schedule_task_statis', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    amount_of_cctasks = models.IntegerField(verbose_name=u'置信任务总数', default=-1)
    completed_cctasks = models.IntegerField(verbose_name=u'置信任务完成数', default=0)
    amount_of_classifytasks = models.IntegerField(verbose_name=u'聚类任务总数', default=-1)
    completed_classifytasks = models.IntegerField(verbose_name=u'聚类任务完成数', default=0)
    amount_of_absenttasks = models.IntegerField(verbose_name=u'查漏任务总数', default=-1)
    completed_absenttasks = models.IntegerField(verbose_name=u'查漏任务完成数', default=0)
    amount_of_pptasks = models.IntegerField(verbose_name=u'逐字任务总数', default=-1)
    completed_pptasks = models.IntegerField(verbose_name=u'逐字任务完成数', default=0)
    amount_of_vdeltasks = models.IntegerField(verbose_name=u'删框任务总数', default=-1)
    completed_vdeltasks = models.IntegerField(verbose_name=u'删框任务完成数', default=0)
    amount_of_reviewtasks = models.IntegerField(verbose_name=u'审定任务总数', default=-1)
    completed_reviewtasks = models.IntegerField(verbose_name=u'审定任务完成数', default=0)
    remark = models.TextField(max_length=256, null=True, blank=True, verbose_name=u'备注', default= '')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = u"切分计划任务统计"
        verbose_name_plural = u"切分计划任务统计管理"
        ordering = ('schedule', )

class Reel_Task_Statistical(models.Model):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='schedule_reel_task_statis',
                                 on_delete=models.SET_NULL, verbose_name=u'切分计划')
    reel = models.ForeignKey(Reel, related_name='reel_tasks_statis')
    amount_of_cctasks = models.IntegerField(verbose_name=u'置信任务总数', default=-1)
    completed_cctasks = models.IntegerField(verbose_name=u'置信任务完成数', default=0)
    amount_of_absenttasks = models.IntegerField(verbose_name=u'查漏任务总数', default=-1)
    completed_absenttasks = models.IntegerField(verbose_name=u'查漏任务完成数', default=0)
    amount_of_pptasks = models.IntegerField(verbose_name=u'逐字任务总数', default=-1)
    completed_pptasks = models.IntegerField(verbose_name=u'逐字任务完成数', default=0)

    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = u"实体卷任务统计"
        verbose_name_plural = u"实体卷任务统计管理"
        ordering = ('schedule', 'reel')
class Task(models.Model):
    '''
    切分校对计划的任务实例
    估计划激活后, 即后台自动据校对类型分配任务列表.
    '''
    number = models.CharField(primary_key=True, max_length=64, verbose_name='任务编号')
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
        verbose_name=u'任务优先级',
        db_index=True,
    )
    update_date = models.DateField(null=True, verbose_name=u'最近处理时间')

    def __str__(self):
        return self.number

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
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务字块数", default=20)
    cc_threshold = models.FloatField("最高置信度")
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='cc_tasks')
    rect_set = JSONField(default=list, verbose_name=u'字块集') # [rect_id, rect_id]

    class Meta:
        verbose_name = u"置信校对任务"
        verbose_name_plural = u"置信校对任务管理"


class ClassifyTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='classify_tasks', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务字块数", default=10)
    char_set = models.TextField(null=True, blank=True, verbose_name=u'字符集')
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='classify_tasks')
    rect_set = JSONField(default=list, verbose_name=u'字块集') # [rect_id, rect_id]

    class Meta:
        verbose_name = u"聚类校对任务"
        verbose_name_plural = u"聚类校对任务管理"

class PageTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='page_tasks', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务页的数量", default=1)
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='page_tasks')
    page_set = JSONField(default=list, verbose_name=u'页的集合') # [page_id, page_id]

    class Meta:
        verbose_name = u"逐字校对任务"
        verbose_name_plural = u"逐字校对任务管理"

class AbsentTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='absent_tasks', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务页的数量", default=1)
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='absent_tasks')
    page_set = JSONField(default=list, verbose_name=u'页的集合') # [page_id, page_id]

    class Meta:
        verbose_name = u"查漏补缺任务"
        verbose_name_plural = u"查漏补缺任务管理"


class DelTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='del_tasks', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务字块数", default=10)
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='del_tasks')
    rect_set = JSONField(default=list, verbose_name=u'字块集') # [deletion_item_id, deletion_item_id]

    class Meta:
        verbose_name = u"删框任务"
        verbose_name_plural = u"删框任务管理"


class ReviewTask(Task):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='review_tasks', on_delete=models.SET_NULL,
                                 verbose_name=u'切分计划')
    count = models.IntegerField("任务字块数", default=10)
    owner = models.ForeignKey(Staff, null=True, blank=True, related_name='review_tasks')
    rect_set = JSONField(default=list, verbose_name=u'字块补丁集') # [patch_id, patch_id]

    class Meta:
        verbose_name = u"审定任务"
        verbose_name_plural = u"审定任务管理"



class DeletionCheckItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    op = models.PositiveSmallIntegerField(verbose_name=u'操作类型', default=OpStatus.DELETED)
    x = models.PositiveSmallIntegerField(verbose_name=u'X坐标', default=0)
    y = models.PositiveSmallIntegerField(verbose_name=u'Y坐标', default=0)
    w = models.PositiveSmallIntegerField(verbose_name=u'宽度', default=1)
    h = models.PositiveSmallIntegerField(verbose_name=u'高度', default=1)
    ocolumn_uri = models.CharField(verbose_name='行图片路径', max_length=128, blank=False)
    ocolumn_x = models.PositiveSmallIntegerField(verbose_name=u'行图X坐标', default=0)
    ocolumn_y = models.PositiveSmallIntegerField(verbose_name=u'行图Y坐标', default=0)
    ch = models.CharField(null=True, blank=True, verbose_name=u'文字', max_length=2, default='')

    rect_id = models.CharField(verbose_name='字块CID', max_length=128, blank=False)
    modifier = models.ForeignKey(Staff, null=True, blank=True, related_name='modify_deletions', verbose_name=u'修改人')
    verifier = models.ForeignKey(Staff, null=True, blank=True, related_name='verify_deletions', verbose_name=u'审定人')
    result = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=u'审定意见', default=ReviewResult.INITIAL)  # 1 同意 2 不同意
    del_task = models.ForeignKey(DelTask, null=True, blank=True, related_name='del_task_items', on_delete=models.SET_NULL,
                                 verbose_name=u'删框任务')
    created_at = models.DateTimeField(verbose_name='删框时间', auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=u'更新时间', auto_now=True)

    class Meta:
        verbose_name = u"删框记录"
        verbose_name_plural = u"删框记录管理"

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


class CharClassifyPlan(models.Model):
    schedule = models.ForeignKey(Schedule, null=True, blank=True, related_name='char_clsfy_plan',
                                 on_delete=models.SET_NULL, verbose_name=u'切分计划')
    ch = models.CharField(null=True, blank=True, verbose_name=u'文字', max_length=2, default='', db_index=True)
    total_cnt = models.IntegerField(verbose_name=u'总数', default=0, db_index=True)
    needcheck_cnt = models.IntegerField(verbose_name=u'待检查数', default=0)
    done_cnt = models.IntegerField(verbose_name=u'已完成数', default=0)
    wcc_threshold = models.DecimalField(verbose_name=u'识别置信阈值',max_digits=4, decimal_places=3, default=0)


    class Meta:
        verbose_name = u"聚类准备表"
        verbose_name_plural = u"聚类准备表管理"

    @classmethod
    def create_charplan(cls, schedule):
        cls.objects.filter(schedule=schedule).all().delete()
        cursor = connection.cursor()
        raw_sql = '''
        SET SEARCH_PATH TO public;
        INSERT INTO public.rect_charclassifyplan (ch, total_cnt, needcheck_cnt, done_cnt, wcc_threshold, schedule_id)
        SELECT
        ch,
        count(rect_rect."ch") as total_cnt,
        0,0,0,
        '%s'
        FROM public.rect_rect
        where reel_id IN ('%s')
        group by ch
        ''' % (schedule.id, '\',\''.join(schedule.reels.values_list('rid', flat=True)))
        cursor.execute(raw_sql)
        cls.objects.filter(schedule=schedule, total_cnt__lt=10).all().delete()


    def measure_charplan(self, wcc_threshold):
        result = Rect.objects.filter(ch=self.ch, reel_id__in=self.schedule.reels.values_list('rid', flat=True)).aggregate(
            needcheck_cnt=Sum(Case(When(wcc__lte=wcc_threshold, then=Value(1)),
            default=Value(0),
            output_field=models.    IntegerField())),
            total_cnt=Count('id'))
        self.total_cnt=result['total_cnt']
        self.needcheck_cnt=result['needcheck_cnt']
        self.wcc_threshold=wcc_threshold
        self.save()


@receiver(post_save, sender=Schedule)
def post_schedule_create_pretables(sender, instance, created, **kwargs):
    if created:
        Schedule_Task_Statistical(schedule=instance).save()
        instance.create_reels_task()
        CharClassifyPlan.create_charplan(instance)

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


