# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-18 09:39
from __future__ import unicode_literals

from django.db import migrations, models


def get_sql(filename):
    with open('rect/sql/' + filename) as f:
        return f.read()

class Migration(migrations.Migration):

    dependencies = [
        ('rect', '0009_auto_20180114_2157'),
    ]

    operations = [
        migrations.RunSQL(
            get_sql('fix_rect_update_slow.sql')
        ,)

    ]