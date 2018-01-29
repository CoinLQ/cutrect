from django.test import TestCase
from rect.models import Schedule, Rect, CCTask, SliceType
from rect.models import Tripitaka, Sutra, Reel, Page, Rect, PageRect

from datetime import date
from django.db import IntegrityError, transaction
from django_bulk_update import helper
from rect.fixtures.rects_data import rect_datas, pagerect_data
from rect.fixtures.gl_rects_data import gl_rect_datas, gl_pagerect_data
from api.serializer import RectSerializer, RectWriterSerializer



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
        cls.prepare_gl()
        cls.prepare_yb()

    @classmethod
    def prepare_yb(cls):
        t = Tripitaka(code="YB", name="永乐北藏")
        t.save()
        t = Tripitaka.objects.get(pk=t.code)
        sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
        sutra.save()
        sutra = Sutra.objects.get(pk=sutra.sutra_sn)

        reel = Reel(sutra=sutra, reel_no=58)
        reel.save()
        reel = Reel.objects.get(pk=reel.reel_sn)
        rects = [Rect(**rect) for rect in rect_datas]
        Rect.objects.bulk_create(rects)
        json =[{'x1': 1200, 'col_id': 'YB000790v001p0001001', 'y': 0, 'y1': 780, 'x': 1131}, {'x1': 1131, 'col_id': 'YB000790v001p0001002', 'y': 0, 'y1': 780, 'x': 1088}, {'x1': 1088, 'col_id': 'YB000790v001p0001003', 'y': 0, 'y1': 780, 'x': 1035}, {'x1': 1035, 'col_id': 'YB000790v001p0001004', 'y': 0, 'y1': 780, 'x': 984}, {'x1': 984, 'col_id': 'YB000790v001p0001005', 'y': 0, 'y1': 780, 'x': 940}, {'x1': 940, 'col_id': 'YB000790v001p0001006', 'y': 0, 'y1': 780, 'x': 891}, {'x1': 891, 'col_id': 'YB000790v001p0001007', 'y': 0, 'y1': 780, 'x': 841}, {'x1': 841, 'col_id': 'YB000790v001p0001008', 'y': 0, 'y1': 780, 'x': 790}, {'x1': 790, 'col_id': 'YB000790v001p0001009', 'y': 0, 'y1': 780, 'x': 744}, {'x1': 744, 'col_id': 'YB000790v001p0001010', 'y': 0, 'y1': 780, 'x': 696}, {'x1': 696, 'col_id': 'YB000790v001p0001011', 'y': 0, 'y1': 780, 'x': 646}, {'x1': 646, 'col_id': 'YB000790v001p0001012', 'y': 0, 'y1': 780, 'x': 598}, {'x1': 598, 'col_id': 'YB000790v001p0001013', 'y': 0, 'y1': 780, 'x': 550}, {'x1': 550, 'col_id': 'YB000790v001p0001014', 'y': 0, 'y1': 780, 'x': 501}, {'x1': 501, 'col_id': 'YB000790v001p0001015', 'y': 0, 'y1': 780, 'x': 452}, {'x1': 452, 'col_id': 'YB000790v001p0001016', 'y': 0, 'y1': 780, 'x': 406}, {'x1': 406, 'col_id': 'YB000790v001p0001017', 'y': 0, 'y1': 780, 'x': 358}, {'x1': 358, 'col_id': 'YB000790v001p0001018', 'y': 0, 'y1': 780, 'x': 310}, {'x1': 310, 'col_id': 'YB000790v001p0001019', 'y': 0, 'y1': 780, 'x': 260}, {'x1': 260, 'col_id': 'YB000790v001p0001020', 'y': 0, 'y1': 780, 'x': 212}, {'x1': 212, 'col_id': 'YB000790v001p0001021', 'y': 0, 'y1': 780, 'x': 164}, {'x1': 164, 'col_id': 'YB000790v001p0001022', 'y': 0, 'y1': 780, 'x': 116}, {'x1': 116, 'col_id': 'YB000790v001p0001023', 'y': 0, 'y1': 780, 'x': 0}]
        page = Page(reel=reel, vol_no=58, page_no=22, json=json)
        page.save()
        PageRect(page_id=page.page_sn, reel_id=reel.reel_sn, line_count=0, column_count=0, rect_set=pagerect_data["char_data"]).save()

    @classmethod
    def prepare_gl(cls):
        t = Tripitaka(code="GL", name="永乐北藏")
        t.save()
        t = Tripitaka.objects.get(pk=t.code)
        sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
        sutra.save()
        sutra = Sutra.objects.get(pk=sutra.sutra_sn)

        reel = Reel(sutra=sutra, reel_no=58)
        reel.save()
        reel = Reel.objects.get(pk=reel.reel_sn)
        rects = [Rect(**rect) for rect in gl_rect_datas]
        Rect.objects.bulk_create(rects)
        json =[{'x1': 1200, 'col_id': 'GL000790r001p0001001', 'y': 0, 'y1': 780, 'x': 1131}, {'x1': 1131, 'col_id': 'GL000790r001p0001002', 'y': 0, 'y1': 780, 'x': 1088}, {'x1': 1088, 'col_id': 'GL000790r001p0001003', 'y': 0, 'y1': 780, 'x': 1035}, {'x1': 1035, 'col_id': 'GL000790r001p0001004', 'y': 0, 'y1': 780, 'x': 984}, {'x1': 984, 'col_id': 'GL000790r001p0001005', 'y': 0, 'y1': 780, 'x': 940}, {'x1': 940, 'col_id': 'GL000790r001p0001006', 'y': 0, 'y1': 780, 'x': 891}, {'x1': 891, 'col_id': 'GL000790r001p0001007', 'y': 0, 'y1': 780, 'x': 841}, {'x1': 841, 'col_id': 'GL000790r001p0001008', 'y': 0, 'y1': 780, 'x': 790}, {'x1': 790, 'col_id': 'GL000790r001p0001009', 'y': 0, 'y1': 780, 'x': 744}, {'x1': 744, 'col_id': 'GL000790r001p0001010', 'y': 0, 'y1': 780, 'x': 696}, {'x1': 696, 'col_id': 'GL000790r001p0001011', 'y': 0, 'y1': 780, 'x': 646}, {'x1': 646, 'col_id': 'GL000790r001p0001012', 'y': 0, 'y1': 780, 'x': 598}, {'x1': 598, 'col_id': 'GL000790r001p0001013', 'y': 0, 'y1': 780, 'x': 550}, {'x1': 550, 'col_id': 'GL000790r001p0001014', 'y': 0, 'y1': 780, 'x': 501}, {'x1': 501, 'col_id': 'GL000790r001p0001015', 'y': 0, 'y1': 780, 'x': 452}, {'x1': 452, 'col_id': 'GL000790r001p0001016', 'y': 0, 'y1': 780, 'x': 406}, {'x1': 406, 'col_id': 'GL000790r001p0001017', 'y': 0, 'y1': 780, 'x': 358}, {'x1': 358, 'col_id': 'GL000790r001p0001018', 'y': 0, 'y1': 780, 'x': 310}, {'x1': 310, 'col_id': 'GL000790r001p0001019', 'y': 0, 'y1': 780, 'x': 260}, {'x1': 260, 'col_id': 'GL000790r001p0001020', 'y': 0, 'y1': 780, 'x': 212}, {'x1': 212, 'col_id': 'GL000790r001p0001021', 'y': 0, 'y1': 780, 'x': 164}, {'x1': 164, 'col_id': 'GL000790r001p0001022', 'y': 0, 'y1': 780, 'x': 116}, {'x1': 116, 'col_id': 'GL000790r001p0001023', 'y': 0, 'y1': 780, 'x': 0}]
        page = Page(reel=reel, reel_no=58, reel_page_no=22, json=json)
        page.save()
        PageRect(page_id=page.page_sn, reel_id=reel.reel_sn, line_count=0, column_count=0, rect_set=gl_pagerect_data["char_data"]).save()


    def test_basic_model_pk_rules(self):
        """
        Tests 藏经基础数据格式.
        """
        with transaction.atomic():
            t = Tripitaka.objects.get(pk='YB')
            sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
            sutra = Sutra.objects.get(pk=sutra.sutra_sn)
            self.assertEquals(sutra.sid, 'YB000790')

            reel = Reel(sutra=sutra, reel_no=58)
            reel = Reel.objects.get(pk=reel.reel_sn)
            self.assertEquals(reel.rid, 'YB000790r058')

            p = Page(reel=reel, vol_no=58, page_no=22)
            page = Page.objects.get(pk=p.page_sn)
            self.assertEquals(page.pid, 'YB000790v058p00220')
            image_path = 'https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/YB/058/YBv058p00220.jpg'
            self.assertEquals(page.get_real_path(), image_path)

            print('ocolumn_sn: YB000790v058p0022001' )

            rect = Rect.generate({'page_code': page.pid, 'reel': page.reel, 'char_no':5 ,'line_no': 10})
            rect = Rect.objects.get(cid=rect.rect_sn)
            print(rect.rect_sn)
            print(rect.column_uri())
            self.assertEquals(rect.reel_id, 'YB000790r058')
            self.assertEquals(rect.rect_sn, 'YB000790v058p0022010n05')

        with transaction.atomic():
            t = Tripitaka.objects.get(pk='GL')
            sutra = Sutra(tripitaka=t, code='79', variant_code='0', name="经名")
            sutra = Sutra.objects.get(pk=sutra.sutra_sn)
            self.assertEquals(sutra.sid, 'GL000790')

            reel = Reel(sutra=sutra, reel_no=58)
            reel = Reel.objects.get(pk=reel.reel_sn)
            self.assertEquals(reel.rid, 'GL000790r058')

            p = Page(reel=reel, reel_no=58, reel_page_no=22)
            page = Page.objects.get(pk=p.page_sn)
            self.assertEquals(page.pid, 'GL000790r058p00220')
            image_path = 'https://s3.cn-north-1.amazonaws.com.cn/lqcharacters-images/GL/000790/058/GL000790r058p00220.jpg'
            self.assertEquals(page.get_real_path(), image_path)
            print('ocolumn_sn: GL000790r058p0022001' )


            rect = Rect(page_code=page.pid, reel=page.reel, char_no=5, line_no=10)
            rect.save()
            rect = Rect.objects.get(cid=rect.rect_sn)
            print(rect.rect_sn)
            print(rect.column_uri())
            self.assertEquals(rect.reel_id, 'GL000790r058')
            self.assertEquals(rect.rect_sn, 'GL000790r058p0022010n05')


    def test_base_rect(self):
        rect = Rect(page_code='YB000321v010p00100', reel_id='YB000790r058', char_no=5, line_no=10)
        rect.cid = rect.rect_sn
        rect.save()
        rect = Rect.objects.get(cid=rect.rect_sn)
        rect = Rect(page_code='GL000321r010p00100', reel_id='GL000790r058', char_no=5, line_no=10)
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
                "col_id": "YB000790v058p0022005",
                "x": 936
            },
            "cid": "YB000790v058p0022005n09",
            "page_code": "YB000790v058p00220",
            "reel_id": "YB000790r058"
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
                "col_id": "YB000790v058p0022008",
                "x": 792
            },
            "cid": "YB000790v058p0022008n03",
            "page_code": "YB000790v058p00220",
            "reel_id": "YB000790r058"
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
        # print(Rect.objects.values_list('cid', flat=True))
        PageRect.reformat_rects('YB000790v058p00220')
        # print(Rect.objects.values_list('cid', flat=True))
        self.assertEquals(Rect.objects.count(), count)

    def test_rebuild_page(self):
        count = len(PageRect.objects.first().rect_set)
        # print(Rect.objects.values_list('cid', flat=True))
        page_rect = PageRect.objects.first()
        page_rect.rebuild_rect()
        # print(Rect.objects.values_list('cid', flat=True))
        # print(Rect.objects.first().__dict__)
        self.assertEquals(len(PageRect.objects.first().rect_set), count)

    def __test_make_pagerect_demo(self):
        Page.objects.filter(pid='YB000790v012p00200')
