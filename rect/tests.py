from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from rect.models import Batch,ORGGroup
from setting.settings import MEDIA_ROOT
import zipfile
import django

import json
class AnimalTestCase(TestCase):
    def setUp(self):
        Batch.objects.create(name='GLZ_CK_HUAYANJING001', series='GLZ', org=ORGGroup.HN, upload=MEDIA_ROOT + '/huanan_test.zip')
        print("setUp zhaopan")

    def test_parse_zipfile(self):
        pass

    def test_parse_zipfile(self):
        """Animals that can speak are correctly identified"""
        print('test_parse_zipfile')
        # batch = Batch()
        # batch.name = 'GLZ_CK_HUAYANJING001'
        # batch.series = 'GLZ'
        # batch.org = ORGGroup.HN
        # batch.upload = MEDIA_ROOT + '/huanan_test.zip'
        # a = batch.save()
        print(MEDIA_ROOT + '/huanan_test.zip')
        upload_file = MEDIA_ROOT + '/huanan_test2.zip'
        zfile = zipfile.ZipFile(upload_file, 'r')
        # TODO 要和用户约定上传文件格式
        for file in zfile.namelist():
            if file.endswith('.txt') :
                with zfile.open(file, 'r') as f:
                    for line in f.readlines():
                        try:
                            ss = str(line, encoding='utf-8')
                            print(ss)
                        except UnicodeDecodeError as error:
                            print(error)


            # names = file.split('.')
            # if names[-1] == 'txt':
            #     #f = zfile.read(file)
            #     f= zfile.open(file, 'r')
            #     line1 = f.readline()
            #     line2 = f.readline()
            #     # f = str(f).encode('utf-8')
            #     # import pdb;pdb.set_trace()
            #     f = str(line2, encoding = "utf-8")
            #     f = f.replace("b'", "")
            #     lines = f.split("\\n")
            #     for line in lines:
            #         self.parsePage(line)