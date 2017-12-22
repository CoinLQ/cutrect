# -*- coding: UTF-8 -*-

import re
import os
import oss2
from rect.models import ORGGroup, SliceType, Batch, PageRect, Rect
import zipfile
import json
from django.db import transaction
from setting.settings import MEDIA_ROOT
from django.contrib.contenttypes.models import ContentType

import base64
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser

# EndPoint: oss-cn-shanghai.aliyuncs.com
# 访问域名: tripitaka.oss-cn-shanghai.aliyuncs.com
# OSS_API_KEY: LTAIyXhhTQhZUhBW
# OSS_API_SECRET: x6jpClbi6gnqMGspFZOPEszCaTB30o
auth = oss2.Auth(os.environ.get('OSS_API_KEY', 'LTAIyXhhTQhZUhBW'), os.environ.get('OSS_API_SECRET', 'x6jpClbi6gnqMGspFZOPEszCaTB30o'))
bucket = oss2.Bucket(auth, 'oss-cn-shanghai.aliyuncs.com', 'tripitaka')

def get_oss_by_name(image_name):
    file_name_list = image_name.split("-")[0].split("_")
    return 'lqhansp/' + "/".join(file_name_list) + "/" + image_name


def UploadImage(local_path):
    filelist = os.listdir(local_path)
    for file_ele in filelist:
        if file_ele.split(".")[-1] == 'jpg':
            bucket.put_object_from_file(get_oss_by_name(file_ele), local_path + file_ele)


def is_img_exist(image_name):
    return bucket.object_exists(get_oss_by_name(image_name))


'''
# 大藏经全名规则-正则描述:
a)	以经为单位组织的藏经按如下规则命名
藏经命名代码_S#####_R###_T####.*
例：高丽藏第1部经第22卷第28页：GLZ_S00001_R022_T0028.jpg
b)	以册为单位组织的藏经按如下规则命名
藏经命名代码_V###_T####.*
例：永乐北藏第1册正文第33页：YLBZ_V001_T0033.png
C）图片名（不含后缀）中不得带有字母、_、数字以外字符
'''
IMG_TYPE_CONFIG = [
    'png',
    'jpg',
    'jpeg'
]
PAGE_URL_SUTRA_RE = r'((?P<series>[A-Z]+)_)?S?(?P<sutra>\d+)_R?(?P<roll>\d+)(_(?P<rollCount>\d+))?_(?P<page>(?P<pageType>[TIPC]?)(?P<pageNum>\d+))\.?(?P<imgType>(?:'+'|'.join(IMG_TYPE_CONFIG).lower()+')?)'
PAGE_URL_VOLUME_RE = r'((?P<series>[A-Z]+)_)?V?(?P<volume>\d+)_(?P<page>(?P<pageType>[TIPC]?)(?P<pageNum>\d+))\.?(?P<imgType>(?:'+'|'.join(IMG_TYPE_CONFIG).lower()+')?)'
pagePatternForSutra = re.compile(PAGE_URL_SUTRA_RE)
pagePatternForVolume = re.compile(PAGE_URL_VOLUME_RE)


def name_to_imgPath(name):
    if name :
        m = pagePatternForSutra.match(name)
        if m : return m.groupdict()
        m = pagePatternForVolume.match(name)
        if m : return m.groupdict()
    return None

def imgPath_to_name(ipo):
    if ipo:
        get = lambda key, prefix='': prefix+ipo[key] if key in ipo and ipo[key] else ''
        name = get('series')
        name += get('volume', '_V') + get('sutra', '_S') + get('roll', '_V')
        name += '_'+ipo['page']
        name += '.'+ipo['imgType'] if 'imgType' in ipo else ''
        return name

def exist_img_on_s3(img, series=''):
    imgPathObj = name_to_imgPath(img)
    if series: imgPathObj['series'] = series
    return imgPathObj and is_img_exist(imgPath_to_name(imgPathObj))

def parseBatch(batch):
    org = int(batch.org)
    parser = None
    if org == ORGGroup.ALI:
        parser = HuaNanBatchParser(batch=batch) #AliBatchParser(batch=batch)
    elif org == ORGGroup.BAIDU:
        parser = HuaNanBatchParser(batch=batch) #BaiDuBatchParser(batch=batch)
    elif org == ORGGroup.HN:
        parser = HuaNanBatchParser(batch=batch)
    if parser: parser.parse()


class BatchParser(object):

    def __init__(self, batch):
        self.batch = batch
        self.notFundImgList = []

    def parse(self, ):
        pass

    def parsePage(self, data):
        pass

    def savePageRect(self, pageRect):
        #return PageRect.objects.create(pageRect)
        return pageRect.save()

    @transaction.atomic
    def saveRectSet(self, rectModelList, pageRect=None, bulk=True):
        pageRect.save()
        for rect in rectModelList:
            rect.page_rect = pageRect
            rect.batch = self.batch
            if not bulk: Rect.objects.create(rect)
        if bulk:
            return Rect.objects.bulk_create(rectModelList)


class HuaNanBatchParser(BatchParser):
    linePattern = re.compile(r'(?P<pageImg>\w+\.jpg) (?P<rectData>.+)\!(?P<txtData>.+)')
    separate = re.compile(';')
    rectPattern = re.compile(r'(?P<x>\d+),(?P<y>\d+),(?P<w>\d+),(?P<h>\d+),(?P<cc>[0-9]+\.[0-9]+)')
    wordPattern = re.compile(r'(?P<word>[\x80-\xff]+)')

    def parse(self):
        upload_file = self.batch.upload
        upload_file_path = os.path.join(MEDIA_ROOT, upload_file.name)
        zfile = zipfile.ZipFile(upload_file_path, 'r')
        # TODO 要和用户约定上传文件格式
        for file in zfile.namelist():
            if file.endswith('.txt'):
                with zfile.open(file, 'r') as f:
                    for line in f.readlines():
                        try:
                            self.parsePage(str(line, encoding='utf-8'))
                        except UnicodeDecodeError as error:
                            print(error) #todo log记录未解析的页数据.

    def parsePage(self, data):
        lineMatcher = self.linePattern.match(data)
        if lineMatcher:
            img = lineMatcher.group('pageImg')
            imgPathObj = name_to_imgPath(img)
            if not 'series' in imgPathObj or not imgPathObj['series'] : imgPathObj['series'] = self.batch.series
            imgPath = imgPath_to_name(imgPathObj)
            # if not imgPath or not is_img_exist(imgPath):
            #     self.notFundImgList.append(img)
            #     return []

            rectData = lineMatcher.group('rectData')
            txtData = lineMatcher.group('txtData')

            rectColumnArr = self.separate.split(rectData)
            txtColumnArr = self.separate.split(txtData)
            #maxColumnCount = max(len(rectColumnArr), len(txtColumnArr))
            columnNum = 0
            maxLineCount = 0
            pageRectSetList = []
            pageRectModelList = []
            for i in range(len(rectColumnArr)): #以切块数据列数为准.
                rectIter = self.rectPattern.finditer(rectColumnArr[columnNum])
                txtColumn = txtColumnArr[columnNum]
                columnNum += 1 #按人类习惯列号以1为开始
                lineNum = 0
                if rectIter:
                    for rect in rectIter:
                        rectDict = rect.groupdict()

                        word = txtColumn[lineNum]
                        if word: rectDict['word'] = word
                        lineNum += 1 #按人类习惯用法行号以1为开始.
                        maxLineCount = max(lineNum, maxLineCount)
                        rectDict['ln'] = lineNum
                        rectDict['cn'] = columnNum
                        rectDict['w'] = int(rectDict['w']) - int(rectDict['x'])
                        rectDict['h'] = int(rectDict['h']) - int(rectDict['y'])
                        pageRectSetList.append(rectDict)
                        model = Rect.generate(rectDict)
                        if model: pageRectModelList.append(model)

            pageRect = PageRect()
            pageRect.batch = self.batch
            pageRect.page = imgPath
            pageRect.column_count = columnNum
            pageRect.line_count = maxLineCount
            pageRect.rect_set = json.dumps(pageRectSetList, ensure_ascii=False)
            # self.savePageRect(pageRect)

            # 批量保存每一列的Rect数据
            self.saveRectSet(pageRectModelList, pageRect)
            return pageRectSetList
        return []


class BaiDuBatchParser(BatchParser):
    def parsePage(self, data):
        pass


class AliBatchParser(BatchParser):
    def parsePage(self, data):
        pass


class AllocateTask(object):

    def __init__(self, schedule):
        self.schedule = schedule

    def allocate(self):
        pass

class CCAllocateTask(AllocateTask):

    def allocate(self):
        CCTask = ContentType.objects.get(app_label='rect', model='cctask').model_class()
        batch = self.schedule.batch
        json_data = json.parser(self.schedule.desc)
        count = json_data['block_size']
        cc_threshold = json_data['cc_val']
        rect_set = []
        task_set = []
        for rect in Rect.objects.filter(batch=batch, cc__lte=cc_threshold):
            rect_set.append(rect.id)
            if len(rect_set) == count:
                task = CCTask(schedule=self.schedule, ttype=SliceType.CC, count=count,
                              rect_set=CCTask.serialize_set(rect_set), cc_threshold=rect.cc)
                rect_set.clear()
                task_set.append(task)
                if len(task_set) == count:
                    CCTask.objects.bulk_create(task_set)
                    task_set.clear()

        CCTask.objects.bulk_create(task_set)



class ClassifyAllocateTask(AllocateTask):

    def allocate(self):
        ClassifyTask = ContentType.objects.get(app_label='rect', model='classifytask').model_class()
        batch = self.schedule.batch
        json_data = json.parser(self.schedule.desc)
        count = json_data['block_size']
        target_char_set = json_data['scope']
        rect_set = []
        word_set = {}
        task_set = []
        if target_char_set == "all":
           query_set = Rect.objects.filter(batch=batch).order_by('word')
        else:
            target_char_set = target_char_set.split(',')
            query_set = Rect.objects.filter(pk__in=target_char_set).order_by('word')

        for rect in query_set:
            rect_set.append(rect.id)
            word_set[rect.word] = 1

            if len(rect_set) == count:
                task = ClassifyTask(schedule=self.schedule, ttype=SliceType.CLASSIFY, count=count,
                                    rect_set=ClassifyTask.serialize_set(rect_set),
                                    char_set=ClassifyTask.serialize_set(word_set.keys()))
                rect_set.clear()
                word_set.clear()
                task_set.append(task)
                if len(task_set) == count:
                    ClassifyTask.objects.bulk_create(task_set)
                    task_set.clear()

        ClassifyTask.objects.bulk_create(task_set)



class PerpageAllocateTask(AllocateTask):

    def allocate(self):
        PageTask = ContentType.objects.get(app_label='rect', model='pagetask').model_class()
        batch = self.schedule.batch
        json_data = json.parser(self.schedule.desc)
        count = json_data['block_size']
        page_header = json_data['page_header']
        if page_header:
            page_regex = r'^'+ page_header + r'.*'
            query_set = PageRect.objects.filter(batch=batch, name__iregex=page_regex)
        else:
            query_set = PageRect.objects.filter(batch=batch)

        page_set = []
        task_set = []
        for page in query_set:
            page_set.append(page.id)
            if len(page_set) == count:
                task = PageTask(schedule=self.schedule, ttype=SliceType.PPAGE, count=count,
                              page_set=PageTask.serialize_set(page_set))
                page_set.clear()
                task_set.append(task)
                if len(task_set) == count:
                    PageTask.objects.bulk_create(task_set)
                    task_set.clear()

        PageTask.objects.bulk_create(task_set)


def allocateTasks(schedule):
    org = int(schedule.org)
    allocator = None
    if org == SliceType.CC: # 置信度
        allocator = CCAllocateTask(schedule)
    elif org == SliceType.CLASSIFY: # 聚类
        allocator = ClassifyAllocateTask(schedule)
    elif org == SliceType.PPAGE: # 逐页浏览
        allocator = PerpageAllocateTask(schedule)
    if allocator:
        allocator.allocate()