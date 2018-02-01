from django.core.management.base import BaseCommand, CommandError
from rect.models import *

class Command(BaseCommand):
    help = 'Migrate sqlite db from xianfu'

    def handle(self, *args, **options):
        tripitakas = [{'code': 'GL', 'name': '高丽藏'},
                      {'code': 'YB', 'name': '永乐北藏'}]
        sutras = [{
                "tripitaka_id": "GL",
                "code": "00079",
                "variant_code": "0",
                "name": "\u5927\u65b9\u5ee3\u4f5b\u83ef\u56b4\u7d93",
                "lqsutra_id": "LQ0310",
                "total_reels": 1
            },
            {
                "tripitaka_id": "YB",
                "code": "00086",
                "variant_code": "0",
                "name": "\u5927\u65b9\u5ee3\u4f5b\u83ef\u56b4\u7d93",
                "lqsutra_id": "LQ0310",
                "total_reels": 1
            }]
        for t in tripitakas:
            Tripitaka(**t).save()

        LQSutra(code="LQ0310", name="\u5927\u65b9\u5ee3\u4f5b\u83ef\u56b4\u7d93", total_reels=1).save()

        for s in sutras:
            Sutra(**s).save()

        # build 高丽藏，暂时没有使用准确数据，每卷按21页，可能会漏几页。
        ql = Sutra.objects.get(pk='GL000790')
        for n in range(1, 3):
                r = Reel(sutra=ql, reel_no=n)
                r.save()
                pages = [Page(reel_id=r.reel_sn, reel_no=n, reel_page_no=pn) for pn in range(1, 22)]
                Page.objects.bulk_create(pages)

         # build 永乐北藏
        yb = Sutra.objects.get(pk='YB000860')
        r = Reel(sutra=yb, reel_no=1)
        r.save()
        vol_no = 27
        page_no_begin = 1
        pages = [Page(reel_id=r.reel_sn, vol_no=vol_no, page_no=pn) for pn in range(page_no_begin, page_no_begin+20)]
        Page.objects.bulk_create(pages)
        for page in Page.objects.all():
            page.down_pagerect()
            page.down_col_pos()
            page_rect = page.pagerects.first()
            if len(page_rect.rect_set)==0:
                print("RECTSET EMPTY! PID:" + page.pid)
                continue
            page_rect.rebuild_rect()
        Reel.objects.all().update(ready = True)