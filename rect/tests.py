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
        json = [{"col_id": "YB_27_c1001", "x": 792, "y": 0, "x1": 1200, "y1": 811}, {"col_id": "YB_27_c1002", "x": 741, "y": 0, "x1": 792, "y1": 811}, {"col_id": "YB_27_c1003", "x": 683, "y": 0, "x1": 741, "y1": 811}, {"col_id": "YB_27_c1004", "x": 624, "y": 0, "x1": 683, "y1": 811}, {"col_id": "YB_27_c1005", "x": 567, "y": 0, "x1": 624, "y1": 811}, {"col_id": "YB_27_c1006", "x": 495, "y": 0, "x1": 567, "y1": 811}, {"col_id": "YB_27_c1007", "x": 435, "y": 0, "x1": 495, "y1": 811}, {"col_id": "YB_27_c1008", "x": 378, "y": 0, "x1": 435, "y1": 811}, {"col_id": "YB_27_c1009", "x": 319, "y": 0, "x1": 378, "y1": 811}, {"col_id": "YB_27_c1010", "x": 264, "y": 0, "x1": 319, "y1": 811}, {"col_id": "YB_27_c1011", "x": 185, "y": 0, "x1": 264, "y1": 811}, {"col_id": "YB_27_c1012", "x": 0, "y": 0, "x1": 185, "y1": 811}, {"col_id": "YB_27_c1013", "x": 795, "y": 811, "x1": 1200, "y1": 1625}, {"col_id": "YB_27_c1014", "x": 744, "y": 811, "x1": 795, "y1": 1625}, {"col_id": "YB_27_c1015", "x": 684, "y": 811, "x1": 744, "y1": 1625}, {"col_id": "YB_27_c1016", "x": 630, "y": 811, "x1": 684, "y1": 1625}, {"col_id": "YB_27_c1017", "x": 573, "y": 811, "x1": 630, "y1": 1625}, {"col_id": "YB_27_c1018", "x": 500, "y": 811, "x1": 573, "y1": 1625}, {"col_id": "YB_27_c1019", "x": 444, "y": 811, "x1": 500, "y1": 1625}, {"col_id": "YB_27_c1020", "x": 380, "y": 811, "x1": 444, "y1": 1625}, {"col_id": "YB_27_c1021", "x": 328, "y": 811, "x1": 380, "y1": 1625}, {"col_id": "YB_27_c1022", "x": 271, "y": 811, "x1": 328, "y1": 1625}, {"col_id": "YB_27_c1023", "x": 0, "y": 811, "x1": 271, "y1": 1625}]
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
        json = [{"col_id": "GL_79_1_c1001", "x": 1131, "y": 0, "x1": 1200, "y1": 780}, {"col_id": "GL_79_1_c1002", "x": 1088, "y": 0, "x1": 1131, "y1": 780}, {"col_id": "GL_79_1_c1003", "x": 1035, "y": 0, "x1": 1088, "y1": 780}, {"col_id": "GL_79_1_c1004", "x": 984, "y": 0, "x1": 1035, "y1": 780}, {"col_id": "GL_79_1_c1005", "x": 940, "y": 0, "x1": 984, "y1": 780}, {"col_id": "GL_79_1_c1006", "x": 891, "y": 0, "x1": 940, "y1": 780}, {"col_id": "GL_79_1_c1007", "x": 841, "y": 0, "x1": 891, "y1": 780}, {"col_id": "GL_79_1_c1008", "x": 790, "y": 0, "x1": 841, "y1": 780}, {"col_id": "GL_79_1_c1009", "x": 744, "y": 0, "x1": 790, "y1": 780}, {"col_id": "GL_79_1_c1010", "x": 696, "y": 0, "x1": 744, "y1": 780}, {"col_id": "GL_79_1_c1011", "x": 646, "y": 0, "x1": 696, "y1": 780}, {"col_id": "GL_79_1_c1012", "x": 598, "y": 0, "x1": 646, "y1": 780}, {"col_id": "GL_79_1_c1013", "x": 550, "y": 0, "x1": 598, "y1": 780}, {"col_id": "GL_79_1_c1014", "x": 501, "y": 0, "x1": 550, "y1": 780}, {"col_id": "GL_79_1_c1015", "x": 452, "y": 0, "x1": 501, "y1": 780}, {"col_id": "GL_79_1_c1016", "x": 406, "y": 0, "x1": 452, "y1": 780}, {"col_id": "GL_79_1_c1017", "x": 358, "y": 0, "x1": 406, "y1": 780}, {"col_id": "GL_79_1_c1018", "x": 310, "y": 0, "x1": 358, "y1": 780}, {"col_id": "GL_79_1_c1019", "x": 260, "y": 0, "x1": 310, "y1": 780}, {"col_id": "GL_79_1_c1020", "x": 212, "y": 0, "x1": 260, "y1": 780}, {"col_id": "GL_79_1_c1021", "x": 164, "y": 0, "x1": 212, "y1": 780}, {"col_id": "GL_79_1_c1022", "x": 116, "y": 0, "x1": 164, "y1": 780}, {"col_id": "GL_79_1_c1023", "x": 0, "y": 0, "x1": 116, "y1": 780}]
        page = Page(reel=reel, reel_no=58, reel_page_no=22, json=json)
        page.save()
        PageRect(page_id=page.page_sn, reel_id=reel.reel_sn, line_count=0, column_count=0, rect_set=gl_pagerect_data["char_data"]).save()

    def test_oldid2s3id(self):
        # YB000010v001p000010 -> YB000010_1_p10
        self.assertEquals(Page.convertSN_to_S3ID('YB000010v001p000010'), 'YB000010_1_p10')
        # YB00001av001p00001a -> YB00001a_1_p1a
        self.assertEquals(Page.convertSN_to_S3ID('YB00001av001p00001a'), 'YB00001a_1_p1a')
        # GL000010r003p001230 -> GL000010_1_3_p1230
        self.assertEquals(Page.convertSN_to_S3ID('GL000010r003p001230'), 'GL000010_1_3_p1230')
        # GL00001ar003p00123a -> GL00001a_1_3_p1230
        self.assertEquals(Page.convertSN_to_S3ID('GL00001ar003p00123a'), 'GL00001a_1a_3_p123a')
        # JX000010e123v123p001230 -> JX000010_123_123_p1230
        self.assertEquals(Page.convertSN_to_S3ID('JX000010e123v123p001230'), 'JX000010_123_123_p1230')
        # JX00001ae020v023p00123a -> JX00001a_20_23_p123a
        self.assertEquals(Page.convertSN_to_S3ID('JX00001ae020v023p00123a'), 'JX00001a_20_23_p123a')

    def tests3id_topath(self):
        # YB000010_1_p10 -> YB/1/YB_1_1
        self.assertEquals(Page.sid_to_uri('YB000010_1_p10'), 'YB/1/YB_1_1')
        # YB000010_1_p1a -> YB/1/YB_1_1a
        self.assertEquals(Page.sid_to_uri('YB000010_1_p1a'), 'YB/1/YB_1_1a')
        # GL000010_1_3_p1230 -> GL/1/3/GL_1_3_123
        self.assertEquals(Page.sid_to_uri('GL000010_1_3_p1230'), 'GL/1/3/GL_1_3_123')
        # GL00001a_1a_3_p123a -> GL/1a/3/GL_1a_3_123a
        self.assertEquals(Page.sid_to_uri('GL00001a_1a_3_p123a'), 'GL/1a/3/GL_1a_3_123a')
        # JX000010_123_123_p1230 -> JX/123/123/JX_123_123_123
        self.assertEquals(Page.sid_to_uri('JX000010_123_123_p1230'), 'JX/123/123/JX_123_123_123')
        # JX00001a_20_23_p123a -> JX/20/23/JX_20_23_123a
        self.assertEquals(Page.sid_to_uri('JX00001a_20_23_p123a'), 'JX/20/23/JX_20_23_123a')

    def test_s3col_topath(self):
        self.assertEquals(Rect.column_uri_path('GL_79_1_c1001'), 'https://s3.cn-north-1.amazonaws.com.cn/lqdzj-col/GL/79/1/GL_79_1_c1001.jpg')


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
            self.assertEquals(page.pid, 'YB000790v058p000220')
            image_path = 'https://s3.cn-north-1.amazonaws.com.cn/lqdzj-image/YB/58/YB_58_22.jpg'
            self.assertEquals(page.get_real_path(), image_path)


            rect = Rect.generate({'page_code': page.pid, 'reel': page.reel, 'char_no':5 ,'line_no': 10})
            rect = Rect.objects.get(cid=rect.rect_sn)
            print(rect.rect_sn)
            print(rect.column_uri())
            self.assertEquals(rect.reel_id, 'YB000790r058')
            self.assertEquals(rect.rect_sn, 'YB000790v058p00022010n05')

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
            self.assertEquals(page.pid, 'GL000790r058p000220')
            image_path = 'https://s3.cn-north-1.amazonaws.com.cn/lqdzj-image/GL/79/58/GL_79_58_22.jpg'
            self.assertEquals(page.get_real_path(), image_path)


            rect = Rect(page_code=page.pid, reel=page.reel, char_no=5, line_no=10)
            rect.save()
            rect = Rect.objects.get(cid=rect.rect_sn)
            print(rect.rect_sn)
            print(rect.column_uri())
            self.assertEquals(rect.reel_id, 'GL000790r058')
            self.assertEquals(rect.rect_sn, 'GL000790r058p00022010n05')


    def test_base_rect(self):
        rect = Rect(page_code='YB000321v010p000100', reel_id='YB000790r058', char_no=5, line_no=10)
        rect.cid = rect.rect_sn
        rect.save()
        rect = Rect.objects.get(cid=rect.rect_sn)
        rect = Rect(page_code='GL000321r010p000100', reel_id='GL000790r058', char_no=5, line_no=10)
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
                "col_id": "YB000790v058p00022005",
                "x": 936
            },
            "cid": "YB000790v058p00022005n09",
            "page_code": "YB000790v058p000220",
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
                "col_id": "YB000790v058p00022008",
                "x": 792
            },
            "cid": "YB000790v058p00022008n03",
            "page_code": "YB000790v058p000220",
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
        PageRect.reformat_rects('YB000790v058p000220')
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
        Page.objects.filter(pid='YB000790v012p000200')
