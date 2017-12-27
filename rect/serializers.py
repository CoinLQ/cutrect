# -*- coding: UTF-8 -*-

from .models import *
from rest_framework import serializers

class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = '__all__'


class PageRectSerializer(serializers.HyperlinkedModelSerializer):
    rects = RectSerializer(many=True)

    def to_representation(self, instance):
        '''
            to_representation 将从 Model 取出的数据 parse 给 Api
            to_internal_value 将客户端传来的 json 数据 parse 给 Model
            当请求版本列表时, 不显示版本的目录信息.
            参考: https://github.com/dbrgn/drf-dynamic-fields/blob/master/drf_dynamic_fields/__init__.py
        '''
        request = self.context['request']
        if request.resolver_match.url_name == 'pagerect-list' and 'rects' in self.fields:
            self.fields.pop('rects')
        return super().to_representation(instance)

    class Meta:
        model = PageRect
        fields = '__all__'


class BatchSerializer(serializers.HyperlinkedModelSerializer):
    pagerects = PageRectSerializer(many=True)

    def to_representation(self, instance):
        '''
            to_representation 将从 Model 取出的数据 parse 给 Api
            to_internal_value 将客户端传来的 json 数据 parse 给 Model
            当请求版本列表时, 不显示版本的目录信息.
            参考: https://github.com/dbrgn/drf-dynamic-fields/blob/master/drf_dynamic_fields/__init__.py
        '''
        request = self.context['request']
        if request.resolver_match.url_name == 'batch-list' and 'pagerects' in self.fields:
            self.fields.pop('pagerects')
        return super().to_representation(instance)

    class Meta:
        model = Batch
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class CCTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = CCTask
        fields = '__all__'


class ClassifyTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifyTask
        fields = '__all__'



class PageTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageTask
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'

class OColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OColumn
        fields = '__all__'

class OPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OPage
        fields = '__all__'


# class PatchSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Patch
#         fields = '__all__'


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#         fields = ('url', 'username', 'email', 'groups')
#
#
# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Group
#         fields = ('url', 'name')