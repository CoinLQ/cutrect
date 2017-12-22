# -*- coding: UTF-8 -*-

from django import forms
from datetime import date
import os
import base64
from .models import Batch, Schedule
from .utils import parseBatch
import hashlib
from setting.settings import MEDIA_ROOT
from django.core.files.storage import default_storage
from rect.tasks import parseBatchToPageRect, add


class BatchModelForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'series', 'org', 'upload', 'remark')
        model = Batch
        widgets = {
            'upload': forms.FileInput(attrs={'accept': 'application/zip'}),
        }

    submit_date = forms.DateField(label='日期', initial=date.today, disabled=True)

    def create(self, commit=True):
        pass

    def save(self, commit=True):
        return super(BatchModelForm, self).save(commit=commit)

        # def save(self, commit=True):
    #     existed = False
    #     upload_field = self.cleaned_data.get('upload', None)
    #     this_md5 = hashlib.md5(base64.b64encode(upload_field.read())).digest()
    #     # for file in os.listdir(MEDIA_ROOT):
    #     #     tmp_md5 = hashlib.md5(base64.b64encode(open(MEDIA_ROOT + file, 'rb').read())).digest()
    #     #     if tmp_md5 == this_md5:
    #     #         existed = True
    #     #         break
    #
    #     b = self.instance
    #     b.org = self.data['org']
    #     b.remark = self.data['remark']
    #
    #     b.save()
    #     if existed:
    #         pass
    #     else:
    #         with default_storage.open(upload_field.name, 'wb+') as destination:
    #             for chunk in upload_field.chunks():
    #                 destination.write(chunk)
    #         # parseBatch(b)
    #         # put_zip_into_db(b, upload_field)
    #
    #     return super(BatchModelForm, self).save(commit=commit)


class ScheduleModelForm(forms.ModelForm):
    def create(self, commit=True):
        pass

    def save(self, commit=True):
        return super(BatchModelForm, self).save(commit=commit)

    class Meta:
        fields = ('batch', 'name', 'type', 'desc', 'user_group', 'status', 'end_date', 'remark')
        model = Schedule
