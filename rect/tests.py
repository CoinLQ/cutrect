from django.test import TestCase
from rect.models import ORGGroup, Schedule, Rect, CCTask, SliceType
from rect.models import Tripitaka, Sutra, Reel, Page, Rect, PageRect
from setting.settings import MEDIA_ROOT

from datetime import date
from rect.utils import allocateTasks, parseBatch
from django.db import IntegrityError, transaction
from django_bulk_update import helper
from rect.fixtures.rects_data import rect_datas, pagerect_data
from api.serializer import RectSerializer, RectWriterSerializer

class ScheduleTestCase(TestCase):
    fixtures = ''
    def setUp(self):
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



from django.db import connection
from django.utils.functional import partition

def bulk_update(model, instances, update_fields=None):
    instances, create = partition(lambda obj: obj.pk is None, instances)
    set_fields = ', '.join(
        ('%(field)s=update_{table}.column%(i)s' % {'field': field, 'i': i + 2})
        for i, field in enumerate(update_fields)
    )
    value_placeholder = '({})'.format(', '.join(['%s'] * (len(update_fields) + 1)))
    values = ','.join([value_placeholder] * len(instances))
    query = ' '.join([
        'UPDATE {table} SET ',
        set_fields,
        'FROM (VALUES ', values, ') update_{table}',
        'WHERE {table}.{pk} = update_{table}.column1'
    ]).format(table=model._meta.db_table, pk=model._meta.pk.get_attname_column()[1])
    print(query)
    params = []
    for instance in instances:
        params.append(instance.pk)
        for field in update_fields:
            params.append(getattr(instance, field))

    connection.cursor().execute(query, params)


class BaseModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        t = Tripitaka(code="GZ", name="高丽藏")
        t.save()
        t = Tripitaka.objects.get(pk=t.code)
        sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
        sutra.save()
        sutra = Sutra.objects.get(pk=sutra.sutra_sn)

        reel = Reel(sutra=sutra, reel_no='58')
        reel.save()
        reel = Reel.objects.get(pk=reel.reel_sn)
        rects = [Rect(**rect) for rect in rect_datas]
        Rect.objects.bulk_create(rects)
        json =[{'x1': 1200, 'col_id': 'GZ000790v001p0001001', 'y': 0, 'y1': 780, 'x': 1131}, {'x1': 1131, 'col_id': 'GZ000790v001p0001002', 'y': 0, 'y1': 780, 'x': 1088}, {'x1': 1088, 'col_id': 'GZ000790v001p0001003', 'y': 0, 'y1': 780, 'x': 1035}, {'x1': 1035, 'col_id': 'GZ000790v001p0001004', 'y': 0, 'y1': 780, 'x': 984}, {'x1': 984, 'col_id': 'GZ000790v001p0001005', 'y': 0, 'y1': 780, 'x': 940}, {'x1': 940, 'col_id': 'GZ000790v001p0001006', 'y': 0, 'y1': 780, 'x': 891}, {'x1': 891, 'col_id': 'GZ000790v001p0001007', 'y': 0, 'y1': 780, 'x': 841}, {'x1': 841, 'col_id': 'GZ000790v001p0001008', 'y': 0, 'y1': 780, 'x': 790}, {'x1': 790, 'col_id': 'GZ000790v001p0001009', 'y': 0, 'y1': 780, 'x': 744}, {'x1': 744, 'col_id': 'GZ000790v001p0001010', 'y': 0, 'y1': 780, 'x': 696}, {'x1': 696, 'col_id': 'GZ000790v001p0001011', 'y': 0, 'y1': 780, 'x': 646}, {'x1': 646, 'col_id': 'GZ000790v001p0001012', 'y': 0, 'y1': 780, 'x': 598}, {'x1': 598, 'col_id': 'GZ000790v001p0001013', 'y': 0, 'y1': 780, 'x': 550}, {'x1': 550, 'col_id': 'GZ000790v001p0001014', 'y': 0, 'y1': 780, 'x': 501}, {'x1': 501, 'col_id': 'GZ000790v001p0001015', 'y': 0, 'y1': 780, 'x': 452}, {'x1': 452, 'col_id': 'GZ000790v001p0001016', 'y': 0, 'y1': 780, 'x': 406}, {'x1': 406, 'col_id': 'GZ000790v001p0001017', 'y': 0, 'y1': 780, 'x': 358}, {'x1': 358, 'col_id': 'GZ000790v001p0001018', 'y': 0, 'y1': 780, 'x': 310}, {'x1': 310, 'col_id': 'GZ000790v001p0001019', 'y': 0, 'y1': 780, 'x': 260}, {'x1': 260, 'col_id': 'GZ000790v001p0001020', 'y': 0, 'y1': 780, 'x': 212}, {'x1': 212, 'col_id': 'GZ000790v001p0001021', 'y': 0, 'y1': 780, 'x': 164}, {'x1': 164, 'col_id': 'GZ000790v001p0001022', 'y': 0, 'y1': 780, 'x': 116}, {'x1': 116, 'col_id': 'GZ000790v001p0001023', 'y': 0, 'y1': 780, 'x': 0}]
        page = Page(reel=reel, vol_no="58", page_no=22, json=json, img_path='some_uri')
        page.save()
        PageRect(page=Page.objects.first(), reel_id=reel.reel_sn, line_count=0, column_count=0, rect_set=pagerect_data["char_data"]).save()


    def test_basic_model_pk_rules(self):
        """
        Tests 藏经基础数据格式.
        """
        with transaction.atomic():
            t = Tripitaka.objects.get(pk='GZ')
            sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
            sutra = Sutra.objects.get(pk=sutra.sutra_sn)
            self.assertEquals(sutra.sid, 'GZ000790')

            reel = Reel(sutra=sutra, reel_no='58')
            reel = Reel.objects.get(pk=reel.reel_sn)
            self.assertEquals(reel.rid, 'GZ000790r058')

            p = Page(reel=reel, vol_no="58", page_no=22, img_path='some_uri')
            page = Page.objects.get(pk=p.page_sn)
            self.assertEquals(page.pid, 'GZ000790v058p00220')

            print('ocolumn_sn: GZ000790v058p0022001' )


            rect = Rect(page_code=page.pid, reel=page.reel, char_no=5, line_no=10)
            rect.save()
            rect = Rect.objects.get(cid=rect.rect_sn)
            print(rect.rect_sn)
            self.assertEquals(rect.reel_id, 'GZ000790r058')
            self.assertEquals(rect.rect_sn, 'GZ000790v058p0022010n05')


    def test_base_rect(self):
        rect = Rect(page_code='YB000321v010p00100', reel_id='GZ000790r058', char_no=5, line_no=10)
        rect.cid = rect.rect_sn
        rect.save()
        rect = Rect.objects.get(cid=rect.rect_sn)

    def test_bulk_create_rect(self):
        count = Rect.objects.count()
        rects =  [{
            "w": 34,
            "line_no": 5,
            "ch": "德",
            "wcc": 0.999976,
            "op": 3,
            "cc": 0.999976,
            "x": 944,
            "ts": "",
            "char_no": 9,
            "h": 28,
            "y": 372,
            "column_set": {
                "x1": 987,
                "y1": 780,
                "y": 0,
                "col_id": "GZ000790v058p0022005",
                "x": 936
            },
            "cid": "GZ000790v058p0022005n09",
            "page_code": "GZ000790v058p00220",
            "reel_id": "GZ000790r058"
        },
        {
            "w": 34,
            "line_no": 8,
            "ch": "衆",
            "wcc": 0.999971,
            "op": 3,
            "cc": 0.999971,
            "x": 796,
            "ts": "",
            "char_no": 3,
            "h": 30,
            "y": 176,
            "column_set": {
                "x1": 842,
                "y1": 780,
                "y": 0,
                "col_id": "GZ000790v058p0022008",
                "x": 792
            },
            "cid": "GZ000790v058p0022008n03",
            "page_code": "GZ000790v058p00220",
            "reel_id": "GZ000790r058"
        }]
        Rect.bulk_insert_or_replace(rects)
        self.assertEquals(Rect.objects.count(), count+2)


    def test_bulk_update_rect(self):
        rects = [rect.serialize_set for rect in Rect.objects.all()]
        for r in rects[:10]:
            r['id'] = None
        for r in rects:
            r['x']=10000
        rectset = RectWriterSerializer(data=rects, many=True)
        rectset.is_valid()
        Rect.bulk_insert_or_replace(rectset.data)
        all_changed = Rect.objects.filter(x=10000).count()
        print(all_changed)
        self.assertEquals(Rect.objects.count(), all_changed+10)

    def test_reformat_page(self):
        count = Rect.objects.count()
        print(Rect.objects.values_list('cid', flat=True))
        PageRect.reformat_rects('GZ000790v058p00220')
        print(Rect.objects.values_list('cid', flat=True))
        self.assertEquals(Rect.objects.count(), count)

    def test_rebuild_page(self):
        count = len(PageRect.objects.first().rect_set)
        print(Rect.objects.values_list('cid', flat=True))
        page_rect = PageRect.objects.first()
        page_rect.rebuild_rect()
        print(Rect.objects.values_list('cid', flat=True))
        print(Rect.objects.first().__dict__)
        self.assertEquals(Rect.objects.count(), count)

    def test_make_pagerect_demo(self):
        Page.objects.filter(pid='GZ000790v012p00200')
    