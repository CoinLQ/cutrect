from rest_framework import serializers
from rect.models import Rect, PageRect


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        can_write_fields = ('x', 'y', 'w', 'h', 'op', 'ch', 'id')
        fields = ('cncode', 'w', 'line_no', 'ch', 'wcc', 'op', 'cc',
                  'x', 'id', 'ts', 'char_no', 'h', 'y', 'column_set')


class PageRectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRect
        fields = ('id', 'code', 'json_rects', 'column_count')
