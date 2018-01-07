from django.test import TestCase
from rect.models import ORGGroup, Schedule, Rect, CCTask, SliceType
from rect.models import Tripitaka, Sutra, Reel, Page, OColumn, Rect
from setting.settings import MEDIA_ROOT

from datetime import date
from rect.utils import allocateTasks, parseBatch


class ScheduleTestCase(TestCase):
    fixtures = ''
    def setUp(self):
        #创建批次数据.
        self.batch = Batch.objects.create(name=u'批次001',
                                     series='GLZ',
                                     org=ORGGroup.HN,
                                     upload=MEDIA_ROOT + '/huanan_test.zip',
                                     )

        #创建切分计划.
        self.schedule = Schedule.objects.create(name=u'华严经第一卷切分计划',
                                           type=SliceType.PPAGE,
                                           batch=self.batch,
                                           desc="{\"block_size\":2, \"cc_threshold\": 1.0}",
                                           status=1,
                                           end_date=date(2017, 12, 31),
                                           user_group=u'北辰精舍',
                                           remark=u'华严经第一卷切分计划_by_北辰精舍团队')

    #测试解析华南数据.
    def _test_parse_batch(self):
        parseBatch(self.batch)
        self.assertEquals(Rect.objects.count(), 8)
        #import pdb; pdb.set_trace()

    #测试分配任务
    def _test_allocate_task(self):
        self.assertEquals(Rect.objects.count(), 8)
        allocateTasks(schedule=self.schedule)
        self.assertEquals(CCTask.objects.count(), 8)


class BaseModelTest(TestCase):

    def test_basic_model_pk_rules(self):
        """
        Tests 藏经基础数据格式.
        """
        t = Tripitaka(code="YB", name="永乐北藏")
        t.save()
        t = Tripitaka.objects.get(pk=t.code)
        sutra = Sutra(tripitaka=t, code='32', variant_code='1', name="经名")
        sutra.save()
        sutra = Sutra.objects.get(pk=sutra.sutra_sn)
        self.assertEquals(sutra.sid, 'YB000321')

        reel = Reel(sutra=sutra, reel_no='1')
        reel.save()
        reel = Reel.objects.get(pk=reel.reel_sn)
        print(reel.reel_sn)
        self.assertEquals(reel.rid, 'YB000321r001')

        p = Page(reel=reel, vol_no="10", page_no=10, img_path='some_uri')
        p.save()

        page = Page.objects.get(pk=p.page_sn)
        self.assertEquals(page.pid, 'YB000321v010p00100')

        ocolumn = OColumn(page=page, line_no=1)
        ocolumn.save()

        ocolumn = OColumn.objects.get(pk=ocolumn.ocolumn_sn)
        print(ocolumn.ocolumn_sn)
        self.assertEquals(ocolumn.oclid, 'YB000321v010p0010001')


        rect = Rect(page_code=page.pid, reel=page.reel, char_no=5, line_no=10)
        rect.save()
        rect = Rect.objects.get(pk=rect.rect_sn)
        print(rect.rect_sn)
        self.assertEquals(rect.reel_id, 'YB000321r001')
        self.assertEquals(rect.rect_sn, 'YB000321v010p0010010n05')

