from setting import celery_app
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('every_minute') every 60 seconds.
    sender.add_periodic_task(60.0, every_minute.s(), name='add every minute')

    # Executes every day at 1:02 a.m.
    sender.add_periodic_task(
        crontab(hour='1', minute='02', day_of_week="*"),
        every_morning.s(), name='good morning')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(10.0, test.s('abc'), expires=10)


@celery_app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@celery_app.task
def every_morning():
    from rect.tasks import clean_daily_page
    clean_daily_page()
    return 'good morning'

@celery_app.task
def every_minute():
    return 'every_minute'

@celery_app.task
def test(arg):
    print(arg)