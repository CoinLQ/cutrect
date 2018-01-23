from rect.models import *
from django.db.models import Min, Sum
from django.db import connection, transaction


class AllocateTask(object):
    class Config:
        CCTASK_COUNT = 20
        DEFAULT_COUNT = 20
        BULK_TASK_COUNT = 30
        PAGETASK_COUNT = 1

    def __init__(self, schedule, reel = None):
        self.schedule = schedule
        self.reel = reel

    def allocate(self):
        pass

    def task_id(self):
        cursor = connection.cursor()
        cursor.execute("select nextval('task_seq')")
        result = cursor.fetchone()
        return result[0]

class CCAllocateTask(AllocateTask):
    def allocate(self):
        reel = self.reel
        query_set = reel.rects.filter(cc__lte=self.schedule.cc_threshold)
        count = AllocateTask.Config.CCTASK_COUNT
        rect_set = []
        task_set = []
        total_tasks = 0
        for no, rect in enumerate(query_set, start=1):
            # rect_set.append(rect.id.hex)
            rect_set.append(rect.serialize_set)
            if len(rect_set) == count:
                # 268,435,455可容纳一部大藏经17，280，000个字
                task_no = "%s_%s%05X" % (self.schedule.schedule_no, reel.rid, self.task_id())
                task = CCTask(number=task_no, schedule=self.schedule, ttype=SliceType.CC, count=count, status=TaskStatus.NOT_GOT,
                              rect_set=list(rect_set), cc_threshold=rect.cc)
                rect_set.clear()
                task_set.append(task)
                if len(task_set) == AllocateTask.Config.BULK_TASK_COUNT:
                    CCTask.objects.bulk_create(task_set)
                    total_tasks += len(task_set)
                    task_set.clear()
        if len(rect_set) > 0:
            task_no = "%s_%s%05X" % (self.schedule.schedule_no, reel.rid, self.task_id())
            task = CCTask(number=task_no, schedule=self.schedule, ttype=SliceType.CC, count=count, status=TaskStatus.NOT_GOT,
                            rect_set=list(rect_set), cc_threshold=rect.cc)
            rect_set.clear()
            task_set.append(task)
        CCTask.objects.bulk_create(task_set)
        total_tasks += len(task_set)
        return total_tasks

def batch(iterable, n = 1):
    current_batch = []
    for item in iterable:
        current_batch.append(item)
        if len(current_batch) == n:
            yield current_batch
            current_batch = []
    if current_batch:
        yield current_batch


class ClassifyAllocateTask(AllocateTask):

    def allocate(self):
        rect_set = []
        word_set = {}
        task_set = []
        count = AllocateTask.Config.DEFAULT_COUNT
        reel_ids = self.schedule.reels.values_list('rid', flat=True)
        base_queryset = Rect.objects.filter(reel_id__in=reel_ids)
        total_tasks = 0
        # 首先找出这些计划准备表
        for plans in batch(CharClassifyPlan.objects.filter(schedule=self.schedule), 3):
            # 然后把分组的计划变成，不同分片的queryset组拼接
            questsets = [base_queryset.filter(ch=_plan.ch, wcc__lte=_plan.wcc_threshold) for _plan in plans]
            if len(questsets) > 1:
                queryset = questsets[0].union(*questsets[1:])
            else:
                queryset = questsets[0]
            # 每组去递归补足每queryset下不足20单位的情况
            for no, rect in enumerate(queryset, start=1):
                rect_set.append(rect.serialize_set)
                word_set[rect.ch] = 1

                if len(rect_set) == count:
                    task_no = "%s_%07X" % (self.schedule.schedule_no, self.task_id())
                    task = ClassifyTask(number=task_no, schedule=self.schedule, ttype=SliceType.CLASSIFY, count=count,
                                        status=TaskStatus.NOT_GOT,
                                        rect_set=list(rect_set),
                                        char_set=ClassifyTask.serialize_set(word_set.keys()))
                    rect_set.clear()
                    word_set = {}
                    task_set.append(task)
                    if len(task_set) == AllocateTask.Config.BULK_TASK_COUNT:
                        ClassifyTask.objects.bulk_create(task_set)
                        total_tasks += len(task_set)
                        task_set.clear()
        if len(rect_set) > 0:
            task_no = "%s_%07X" % (self.schedule.schedule_no, self.task_id())
            task = ClassifyTask(number=task_no, schedule=self.schedule, ttype=SliceType.CLASSIFY, count=count,
                                status=TaskStatus.NOT_GOT,
                                rect_set=list(rect_set),
                                char_set=ClassifyTask.serialize_set(word_set.keys()))
            rect_set.clear()
            task_set.append(task)
        ClassifyTask.objects.bulk_create(task_set)
        total_tasks += len(task_set)
        return total_tasks


class PerpageAllocateTask(AllocateTask):

    def allocate(self):
        reel = self.reel
        query_set = filter(lambda x: x.primary, PageRect.objects.filter(reel=reel))

        page_set = []
        task_set = []
        count = AllocateTask.Config.PAGETASK_COUNT
        total_tasks = 0
        for no, pagerect in enumerate(query_set, start=1):
            page_set.append(pagerect.serialize_set)
            if len(page_set) == count:
                task_no = "%s_%s%05X" % (self.schedule.schedule_no, reel.rid, self.task_id())
                task = PageTask(number=task_no, schedule=self.schedule, ttype=SliceType.PPAGE, count=1,
                                  status=TaskStatus.NOT_READY,
                                  page_set=list(page_set))
                page_set.clear()
                task_set.append(task)
                if len(task_set) == AllocateTask.Config.BULK_TASK_COUNT:
                    PageTask.objects.bulk_create(task_set)
                    total_tasks += len(task_set)
                    task_set.clear()

        PageTask.objects.bulk_create(task_set)
        total_tasks += len(task_set)
        return total_tasks


class AbsentpageAllocateTask(AllocateTask):

    def allocate(self):
        reel = self.reel
        # TODO: 缺少缺页查找页面
        queryset = PageRect.objects.filter(reel=reel)
        query_set = filter(lambda x: x.primary, queryset)

        page_set = []
        task_set = []
        count = AllocateTask.Config.PAGETASK_COUNT
        total_tasks = 0
        for no, pagerect in enumerate(query_set, start=1):
            page_set.append(pagerect.serialize_set)
            if len(page_set) == count:
                task_no = "%s_%s%05X" % (self.schedule.schedule_no, reel.rid, self.task_id())
                task = AbsentTask(number=task_no, schedule=self.schedule, ttype=SliceType.CHECK, count=1,
                                page_set=list(page_set))
                page_set.clear()
                task_set.append(task)
                if len(task_set) == AllocateTask.Config.BULK_TASK_COUNT:
                    PageTask.objects.bulk_create(task_set)
                    total_tasks += len(task_set)
                    task_set.clear()

        PageTask.objects.bulk_create(task_set)
        total_tasks += len(task_set)
        return total_tasks


class DelAllocateTask(AllocateTask):

    def allocate(self):
        rect_set = []
        task_set = []
        count = AllocateTask.Config.PAGETASK_COUNT
        total_tasks = 0
        for items in batch(DeletionCheckItem.objects.filter(del_task_id=None), 10):
            if len(items) == 10:
                rect_set = list(map(lambda x:x.pk.hex, items))
                task_no = "%s_%07X" % ('DelTask', self.task_id())
                task = DelTask(number=task_no,  ttype=SliceType.VDEL,
                                rect_set=rect_set)
                rect_set.clear()
                ids = [_item.pk for _item in items]
                DeletionCheckItem.objects.filter(id__in=ids).update(del_task_id=task_no)
                task_set.append(task)
                if len(task_set) == AllocateTask.Config.BULK_TASK_COUNT:
                    DelTask.objects.bulk_create(task_set)
                    total_tasks += len(task_set)
                    task_set.clear()
        DelTask.objects.bulk_create(task_set)
        total_tasks += len(task_set)
        task_set.clear()
        return total_tasks

def allocateTasks(schedule, reel, type):
    allocator = None
    count = -1
    if type == SliceType.CC: # 置信度
        allocator = CCAllocateTask(schedule, reel)
    elif type == SliceType.CLASSIFY: # 聚类
        allocator = ClassifyAllocateTask(schedule)
    elif type == SliceType.PPAGE: # 逐字
        allocator = PerpageAllocateTask(schedule, reel)
    elif type == SliceType.CHECK: # 查漏
        allocator = PerpageAllocateTask(schedule, reel)
    elif type == SliceType.VDEL: # 删框
        allocator = DelAllocateTask(schedule, reel)
    if allocator:
        count = allocator.allocate()
    return count

class GenTask(object):

    @staticmethod
    @transaction.atomic
    def gen_cctask_by_plan():
        for stask in Schedule_Task_Statistical.objects.filter(amount_of_cctasks=-1):
            # 未激活说明，第一步的CC阈值没有填写
            if stask.schedule.status == ScheduleStatus.NOT_ACTIVE:
                continue
            # 逐卷创建任务
            for rtask in Reel_Task_Statistical.objects.filter(schedule=stask.schedule).prefetch_related('reel'):
                if rtask.amount_of_cctasks != -1:
                    continue
                count = allocateTasks(stask.schedule, rtask.reel, SliceType.CC)
                rtask.amount_of_cctasks = count
                rtask.save(update_fields=['amount_of_cctasks'])
            # 检查每卷大于-1，开启总计划，更新任务数。
            quertset = Reel_Task_Statistical.objects.filter(schedule=stask.schedule)
            result = quertset.aggregate(Min('amount_of_cctasks'))
            # 只有所有卷都开启任务，计划表的总任务数才更新。
            if result['amount_of_cctasks__min'] != -1:
                count = quertset.aggregate(Sum('amount_of_cctasks'))['amount_of_cctasks__sum']
                stask.amount_of_cctasks = count
                stask.save(update_fields=['amount_of_cctasks'])

    @staticmethod
    @transaction.atomic
    def gen_classifytask_by_plan():
        for stask in Schedule_Task_Statistical.objects.filter(amount_of_classifytasks=-1):
            # 检查所有准备表的wcc_threshold值都大于0，开启总计划。
            if CharClassifyPlan.objects.filter(wcc_threshold__lte=0).count() > 0:
                continue
            count = allocateTasks(stask.schedule, None, SliceType.CLASSIFY)
            stask.amount_of_classifytasks = count
            stask.save(update_fields=['amount_of_classifytasks'])


    @staticmethod
    @transaction.atomic
    def gen_pptask_by_plan():
        for stask in Schedule_Task_Statistical.objects.filter(amount_of_pptasks=-1):
            # 逐卷创建任务
            for rtask in Reel_Task_Statistical.objects.filter(schedule=stask.schedule).prefetch_related('reel'):
                if rtask.amount_of_pptasks != -1:
                    continue
                count = allocateTasks(stask.schedule, rtask.reel, SliceType.PPAGE)
                rtask.amount_of_pptasks = count
                rtask.save(update_fields=['amount_of_pptasks'])
            # 检查每卷大于-1，开启总计划，更新任务数。
            quertset = Reel_Task_Statistical.objects.filter(schedule=stask.schedule)
            result = quertset.aggregate(Min('amount_of_pptasks'))
            # 只有所有卷都开启任务，计划表的总任务数才更新。
            if result['amount_of_pptasks__min'] != -1:
                count = quertset.aggregate(Sum('amount_of_pptasks'))['amount_of_pptasks__sum']
                stask.amount_of_pptasks = count
                stask.save(update_fields=['amount_of_pptasks'])

    @staticmethod
    @transaction.atomic
    def gen_vdeltask():
        schedule = Schedule.objects.first()
        allocateTasks(schedule, None, SliceType.VDEL)