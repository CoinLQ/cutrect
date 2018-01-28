from django.core.management.base import BaseCommand, CommandError
from sutra.models import *
from rect.models import *

class Command(BaseCommand):
    help = 'Migrate sqlite db from xianfu'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for t in Tripitaka2.objects.all():
            Tripitaka(code=t.code, name=t.name).save()

        for n in LQSutra2.objects.all():
            LQSutra(code=n.code, name=n.name, total_reels=n.total_reels).save()

        # for s in Sutra2.objects.filter(pk__gte=3348):
        #     if (s.tripitaka_id=='GZ'):
        #         s.tripitaka_id='GL'

        #     sutra = Sutra(tripitaka_id=s.tripitaka_id, code=s.code, variant_code=s.variant_code, name=s.name, lqsutra_id=s.lqsutra_id, total_reels=s.total_reels)
        #     if not Sutra.objects.filter(sid=sutra.sutra_sn).first():
        #         sutra.save()

        # for r in Reel2.objects.filter(sutra_id__in=[3348,3349,3350,3351,3352,3353,3355,3356]):
        #     reel = Reel(sutra_id=r.sutra.sid, reel_no=int(r.code))
        #     if not Reel.objects.filter(rid=reel.reel_sn).first():
        #         reel.save()

        # s = Sutra2.objects.get(pk=3354)
        # for n in range(1,46):
        #     Reel(sutra_id=s.sid, reel_no=n).save()
        # for sutra in Sutra.objects.all():
        #     for p in Page2.objects.filter(code__regex='^'+sutra.sid).select_related('reel'):
        #         try:
        #             Page(reel_id=p.reel.reel_sn, vol_no=int(p.v_no), page_no=int(p.v_page_no)).save()
        #         except Exception as e:
        #             pass

        r = Reel2.objects.get(pk=16147)
        s = r.sutra
        s.tripitaka_id='GL'
        sutra = Sutra(tripitaka_id=s.tripitaka_id, code=s.code, variant_code=s.variant_code, name=s.name, lqsutra_id=s.lqsutra_id, total_reels=s.total_reels)
            if not Sutra.objects.filter(sid=sutra.sutra_sn).first():
                sutra.save()
        for p in r.page2_set.all().select_related('reel'):
            Page(reel_id=p.reel.reel_sn, reel_no=int(p.v_no), reel_page_no=int(p.v_page_no)).save()