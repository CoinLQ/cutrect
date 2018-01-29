from django.db import models
import uuid
# Create your models here.
import boto3
from datetime import datetime
import os
from PIL import Image

s3c = boto3.client('s3')
my_bucket = 'lqcharacters-images'
s3 = boto3.resource('s3')



class TripiMixin(object):
    def __str__(self):
        return self.name


class Batch(models.Model):
    sub_date = models.DateField()
    org = models.CharField(max_length=128, blank=False)
    des = models.CharField(max_length=512, blank=False)


class LQSutra2(models.Model, TripiMixin):
    code = models.CharField(verbose_name='龙泉经目编码', max_length=8, primary_key=True)
    # （为"LQ"+ 经序号 + 别本号）
    name = models.CharField(verbose_name='龙泉经目名称', max_length=64, blank=False)
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)

    class Meta:
        verbose_name = u"龙泉经目"
        verbose_name_plural = u"龙泉经目管理"
        db_table = 'sutra_lqsutra'

    def __str__(self):
        return self.name


class Tripitaka2(models.Model, TripiMixin):
    code = models.CharField(verbose_name='实体藏经版本编码', primary_key=True, max_length=4, blank=False)
    name = models.CharField(verbose_name='实体藏经名称', max_length=32, blank=False)

    class Meta:
        verbose_name = '实体藏经'
        verbose_name_plural = '实体藏经管理'
        db_table = 'sutra_tripitaka'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Sutra2(models.Model, TripiMixin):
    sid = models.CharField(verbose_name='实体藏经|唯一经号编码', editable=True, max_length=32)  # 藏经版本编码 + 5位经序号+1位别本号
    tripitaka = models.ForeignKey(Tripitaka2, related_name='sutras', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='实体经目编码', max_length=5, blank=False)
    variant_code = models.CharField(verbose_name='别本编码', max_length=1, default='0')
    name = models.CharField(verbose_name='实体经目名称', max_length=64, blank=True)
    lqsutra = models.ForeignKey(LQSutra2, verbose_name='龙泉经目编码', null=True, blank=True, on_delete=models.CASCADE)  # （为"LQ"+ 经序号 + 别本号）
    total_reels = models.IntegerField(verbose_name='总卷数', blank=True, default=1)

    class Meta:
        verbose_name = '实体经目'
        verbose_name_plural = '实体经目管理'
        db_table = 'sutra_sutra'

    def change_name(self):
        reels = self.reel_set.all()
        for reel in reels:
            reel.change_name()

    def __str__(self):
        return self.sid + self.name


class Reel2(models.Model):
    sutra = models.ForeignKey(Sutra2, on_delete=models.CASCADE)
    code = models.CharField(max_length=128, blank=False)
    name = models.CharField(max_length=128, blank=False)
    ready = models.BooleanField(default=False)
    image_ready = models.BooleanField(default=False)
    #image_ready_no = models.SmallIntegerField(default=0)
    image_upload = models.BooleanField(default=False)
    txt_ready = models.BooleanField(default=False)
    cut_ready = models.BooleanField(default=False)
    column_ready = models.BooleanField(default=False)

    class Meta:
        verbose_name = '卷'
        verbose_name_plural = '卷'
        db_table = 'sutra_reel'

    def __str__(self):
        return self.sutra.tripitaka.code+self.sutra.name + '第' + self.code + '卷'


    @property
    def reel_sn(self):
        return "%sr%s" % (self.sutra.sid, self.code.zfill(3))

    def change_name(self):
        pages = self.page_set.all()
        for page in pages:
            page.change_name()

    def check_image(self):
        pages = self.page_set.all()
        no = 0
        # 用百分比还是布尔值？

    def pdf_2_img(self, pdf_path):
        img_dir = '/'.join([self.sutra.tripitaka.code, self.sutra.sid[2:], 'v%03d' % int(self.code)])
        if not os.path.exists(img_dir):
            os.system('mkdir -p '+img_dir)
        trans_cmd = 'gs  -dQUIET -sDEVICE=jpeg -o ' + img_dir + '/test.jpg -r72  -dFirstPage=1 -dLastPage=1 ' + pdf_path
        os.system(trans_cmd)
        im = Image.open(img_dir + '/test.jpg')
        im.show(title="width:" + str(im.width))
        if im.width < 1200:
            n = 1600 / im.width * 72
        else:
            n = 72
        os.system('rm ' + img_dir + '/test.jpg')
        trans_cmd = 'gs  -dQUIET -sDEVICE=jpeg -o ' + img_dir + '/%04d.jpg -r' + str(int(n)) + ' ' + pdf_path
        os.system(trans_cmd)

    '''def upload_img(self, tripitaka_dir=''):
        pages = self.page_set.all()
        for p in pages:
            p.upload_img(tripitaka_dir)'''


class Page2(models.Model):
    reel = models.ForeignKey(Reel2, on_delete=models.CASCADE)
    code = models.CharField(max_length=128, blank=False)
    v_no = models.IntegerField(blank=True, default=0)
    v_page_no = models.IntegerField(blank=True, default=1)
    r_page_no = models.IntegerField(blank=True, default=1)
    img_path = models.CharField(max_length=128, blank=False)
    ready = models.BooleanField(default=False)
    image_ready = models.BooleanField(default=False)
    image_upload = models.BooleanField(default=False)
    txt_ready = models.BooleanField(default=False)
    cut_ready = models.BooleanField(default=False)
    column_ready = models.BooleanField(default=False)

    class Meta:
        verbose_name = '页'
        verbose_name_plural = '页'
        db_table = 'sutra_page'

    def generate_line(self):
        pass

    def get_real_path(self):
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path

    def change_name(self):
        if len(self.code) != len('QL000010v001p00180'):
            sid = self.reel.sutra.sid
            self.code = sid + 'v%03d' % self.v_no + 'p%04d0' % self.v_page_no
            self.img_path = '/'.join([sid[:2], sid[2:], 'v%03d' % self.v_no, self.code + '.jpg'])
            self.save()


class Column2(models.Model):
    page = models.ForeignKey(Page2, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=128, blank=False)
    img_path = models.CharField(max_length=128, blank=False)

    def get_real_path(self):
        return "https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/" + self.img_path

    class Meta:
        db_table = 'sutra_column'
