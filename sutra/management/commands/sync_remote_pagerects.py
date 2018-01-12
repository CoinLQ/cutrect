from django.core.management.base import BaseCommand, CommandError
from rect.models import *
import datetime
import urllib.request
import urllib

class Command(BaseCommand):
    help = 'Sync All Page\'s pagerects from AWS'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str)

    def try_down_and_create_pagerects(self):
        # 得出切分数据未获得Page
        pages = Page.objects.filter(status__lt=PageStatus.RECT_NOTREADY)
        before_count = pages.count()
        print("unready pages count: {0}".format(before_count))

        # 按卷的组织方式去查找page
        for r in Reel.objects.filter(ready=False):
            for page in r.pages.filter(status__lt=PageStatus.RECT_NOTREADY):
                # 如果今天已尝试下载，将被跳过
                if page.updated_at.date() == datetime.date.today() \
                    and page.status == PageStatus.RECT_NOTFOUND:
                    continue
                # 正式下载并解析
                page.down_pagerect()

        last_count = Page.objects.filter(status__lt=PageStatus.RECT_NOTREADY).count()
        print("imported pages count: {0}".format(before_count-last_count))
        print("download failure pages count: {0}".format(Page.objects.filter(status=PageStatus.RECT_NOTFOUND).count()))
        print("parse failure pages count: {0}".format(Page.objects.filter(status=PageStatus.PARSE_FAILED).count()))


    def dump_failure_json(self):
        for p in Page.objects.filter(status=PageStatus.PARSE_FAILED):
            print(p.pid + ": RECT PARSER Failed")
            print(p.get_real_path())
            print("CONTENT:" + p.json["content"])
        for page in Page.objects.filter(status=PageStatus.RECT_NOTREADY).prefetch_related('pagerects'):
            page_rect = page.pagerects.first()
            if len(page_rect.rect_set)==0:
                page.down_pagerect()
                print("RECTSET EMPTY! PID:" + page.pid)

    def expand_pagerects(self, check_pic = True):
        opener = urllib.request.build_opener()
        for page in Page.objects.filter(status=PageStatus.RECT_NOTREADY).prefetch_related('pagerects'):
            page_rect = page.pagerects.first()
            if len(page_rect.rect_set)==0:
                print("RECTSET EMPTY! PID:" + page.pid)
                continue
            page_rect.rebuild_rect()
            print(page.pid + ": Expand rect done!")
            page.status = PageStatus.COL_PIC_NOTFOUND
            if check_pic:
                try:
                    opener.open(page.get_real_path())
                except urllib.error.HTTPError as e:
                    print(page.pid + ": PIC not found!")
                    page.status = PageStatus.CUT_PIC_NOTFOUND
            page.save()
        print("pages CUT_PIC_NOTFOUND count: {0}".format(Page.objects.filter(status=PageStatus.CUT_PIC_NOTFOUND).count()))

    def expand_pagecols(self, check_pic = True):
        for page in Page.objects.filter(status=PageStatus.COL_PIC_NOTFOUND):
            page.down_col_pos()
        print('done')

    def insert_col2rect(self):
        for page in Page.objects.filter(status=PageStatus.RECT_COL_NOTREADY):
            if(PageRect.reformat_rects(page.pid)):
                page.status = PageStatus.READY
                page.save()
            else:
                print(page.pid + ": RECT_COL not found!")
                page.status = PageStatus.RECT_COL_NOTFOUND
                page.save()
        print('done')

    def mark_ready_reel(self):
        reel_ids = Page.objects.filter(status=PageStatus.READY).values_list('reel_id', flat=True).distinct()
        for reel_id in reel_ids:
            reel = Reel.objects.get(pk=reel_id)
            stats = reel.pages.values_list('status', flat=True).distinct()
            if len(stats) == 1:
                reel.ready = True
                reel.save()
                reel.pages.update(status=PageStatus.MARKED)
            else:
                output = reel.rid + ": Page Statuses have "
                for stat in stats:
                   output +=  PageStatus.CHOICES[stat][1] + " "
                print(output)

    def handle(self, *args, **options):
        which = options['action']
        if (which == 'pagerect'):
            self.try_down_and_create_pagerects()
            print('ok')
        elif(which == 'dump_json'):
            self.dump_failure_json()
        elif(which == 'expand_rects'):
            self.expand_pagerects()
        elif(which == 'expand_cols'):
            self.expand_pagecols()
        elif(which == 'insert_col2rect'):
            self.insert_col2rect()
        elif(which == 'mark_ready_reel'):
            self.mark_ready_reel()
