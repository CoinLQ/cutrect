# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from rect.utils import parseBatch, allocateTasks
from rect.models import Schedule
from setting import celery_app
import os
from django.dispatch import receiver
from django.db import models


# @shared_task
# def parseBatchToPageRect(batchId=''):
#     # 校验url是否正确
#     if batchId:
#         batch = Batch.objects.get(id=batchId)
#         if batch:
#             parseBatch(batch)




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


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
