from rest_framework import serializers
from rect.models import Rect, PageRect


class RectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rect
        fields = ('cncode', 'w', 'line_no', 'ch', 'wcc', 'op', 'cc',
                  'x', 'id', 'ts', 'char_no', 'h', 'y')


class PageRectSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageRect
        fields = ('id', 's3_uri', 'code', 'json_rects', 'column_count')
