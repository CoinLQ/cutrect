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

        for s in Sutra2.objects.filter(pk__gte=3348):
            Sutra(tripitaka_id=s.tripitaka_id, code=s.code, variant_code=s.variant_code, name=s.name, lqsutra_id=s.lqsutra_id, total_reels=s.total_reels).save()


        for r in Reel2.objects.filter(sutra_id__in=[3348,3349,3350,3351,3352,3353,3355,3356]):
            Reel(sutra_id=r.sutra.sid, reel_no=str(r.code)).save()
        s = Sutra2.objects.get(pk=3354)
        for n in range(1,46):
            Reel(sutra_id=s.sid, reel_no=str(n)).save()
        for sutra in Sutra.objects.all():
            for p in Page2.objects.filter(code__regex='^'+sutra.sid).select_related('reel'):
                try:
                    Page(reel_id=p.reel.reel_sn, vol_no=str(p.v_no), page_no=int(p.v_page_no)).save()
                except Exception as e:
                    pass
