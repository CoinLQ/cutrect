from django.test import TestCase
from rect.models import Batch,ORGGroup, Schedule, Rect, CCTask, SliceType

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
    def test_parse_batch(self):
        parseBatch(self.batch)
        self.assertEquals(Rect.objects.count(), 8)
        #import pdb; pdb.set_trace()

    #测试分配任务
    def test_allocate_task(self):
        self.assertEquals(Rect.objects.count(), 8)
        allocateTasks(schedule=self.schedule)
        self.assertEquals(CCTask.objects.count(), 8)

