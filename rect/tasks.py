# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from rect.lib.gen_task import allocateTasks
from rect.models import Schedule
from cutrect import celery_app, email_if_fails
import os
import logging
from django.dispatch import receiver
from django.db import models



@shared_task
def allocateTasksBySchedule(scheduleId=''):
    if scheduleId:
        schedule = Schedule.objects.get(id=scheduleId)
        if schedule:
            allocateTasks(schedule)

@shared_task
def clean_daily_page():
    page_klass = ContentType.objects.get(app_label='rect', model='page').model_class()
    page_klass.objects.filter(locked=1).update(locked=0)


@shared_task(ignore_result=True)
def bg_create_pages(*args):
    pass





@shared_task(ignore_result=True)
@email_if_fails
def dummy_test(**kwargs):
    log = logging.getLogger()

    log.debug("Debug DUMMY TEST")
    log.info("Info DUMMY TEST")
    log.warning("Warning DUMMY TEST")
    log.error("Error DUMMY TEST")
    log.critical("Critical DUMMY TEST")
    Schedule.objects.get(id=9999999)
