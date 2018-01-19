from rest_framework import serializers
from rect.models import Rect, PageRect, DeletionCheckItem


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        can_write_fields = ('x', 'y', 'w', 'h', 'op', 'ch', 'id', 'page_code', 'line_no', 'char_no')
        fields = ('cncode', 'w', 'line_no', 'ch', 'wcc', 'op', 'cc',
                  'x', 'id', 'ts', 'char_no', 'h', 'y', 'column_set', 'cid', 'page_code',
                  'reel_id')

class RectWriterSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(format='hex_verbose')
    class Meta:
        model = Rect
        fields = ('x', 'y', 'w', 'h', 'op', 'ch', 'id', 'page_code', 'line_no', 'char_no')

class PageRectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRect
        fields = ('id', 'code', 'json_rects', 'column_count')


class DeletionCheckItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeletionCheckItem
        can_write_fields = ['id', 'result']
        fields = '__all__'